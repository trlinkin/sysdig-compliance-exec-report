from optparse import OptionParser
import http.client
import os
import urllib.parse
import sys
import json
from datetime import datetime
import unicodedata
import re
import logging


import matplotlib.pyplot as plt
import pdfkit
import markdown2
from bottle import template


TEMPLATES_DIR=f'{os.path.dirname(os.path.realpath(__file__))}/templates'
DATE_PRETTY=datetime.today().strftime("%B %d, %Y at %H:%M %p %Z")
FILE_DATE=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
SDC_SECURE_TOKEN=os.environ.get('SDC_SECURE_TOKEN')
SDC_SECURE_URL=os.environ.get('SDC_SECURE_URL')


def policy_filter(zone, policy=None, page_size=1, page_number=1):

    request_filter = f'?pageNumber={page_number}&pageSize={page_size}&'

    safe_zone = urllib.parse.quote_plus(zone)
    request_filter = f'{request_filter}filter=zone.name="{safe_zone}"'

    if policy:
        policies = policy.split(',')
        policies = [x.strip(' ') for x in policies]
        policy_list = ', '.join(f'"{w}"' for w in policies)

        safe_policy = urllib.parse.quote_plus(policy_list)
        request_filter = f'{request_filter}%20and%20policy.name%20in%20({safe_policy})'

    logging.debug('Calculated API request filter -- {}'.format(request_filter))

    return request_filter


def get_report(secure_base_url, secure_api_token, filter=""):
    headers = {"Authorization": "Bearer " + secure_api_token,
               "Accept": "application/json"}

    conn = http.client.HTTPSConnection(secure_base_url)

    url = f"/api/cspm/v1/compliance/requirements{filter}"

    try:
        conn.request("GET", url, None, headers)
        res = conn.getresponse()
        if res.status != 200:
            logging.error('Error {} from the Sysdig Console'.format(res.status))
    
    except RequestException as e:
        logging.error('Error during requests to {}: {}'.format(url, str(e)))
        sys.exit(2)
    
    data = res.read()

    report_dict = json.loads(data)
    return report_dict

def convert_report(report):
    new_report = {}

    for req in report['data']:
        if req['policyName'] not in new_report:
            new_report[req['policyName']] = {'fail':[],
                                             'pass':[],
                                             'policyId': req['policyId'],
                                             'normalizedName': normalize_policy_name(req['policyName'])}

        if req['pass']:
            sort = 'pass'
        else:
            sort = 'fail'

        new_report[req['policyName']][sort].append(req)

    logging.debug('Converted report data contains {} policies'.format(len(new_report)))

    return new_report

#stolen with glee from the markdown2 lib, this is how they do it, I need to do it too
def normalize_policy_name(name):
    value = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    value = re.compile(r'[^\w\s-]').sub('', value).strip().lower()
    return re.compile(r'[-\s]+').sub('-', value)

def load_templates():
    full_template = ""
    template_listing_file = open(f'{TEMPLATES_DIR}/templates.json', 'r')
    template_list = json.load(template_listing_file)

    for template in template_list:
        logging.debug('Reading in template chunk {} from {}'.format(TEMPLATES_DIR,template))
        template_chunk_file = open(f'{TEMPLATES_DIR}/{template}', 'r')
        full_template += "\n" + template_chunk_file.read()

    return full_template

def make_charts(report):
    for pol in report.keys():
        labels = ["Passing","Failing"]
        values = [len(report[pol]['pass']), len(report[pol]['fail'])]
        make_pie("pol-" + report[pol]['policyId'], labels, values)

        failure_step = 1
        for req in report[pol]['fail']:
            labels = ["Passing","Failing"]
            values = [(len(req['controls']) - req['failedControls']),req['failedControls']]
            make_pie("req-" + req['requirementId'], labels, values, shade = failure_step %2)
            failure_step += 1

def make_pie(chart, labels, values, shade = 0):
    colors = ["#20DC9D", "#FF7774"]
    plt.clf()
    plt.pie(values, labels=labels, labeldistance=1.15, shadow=False, startangle=90, colors=colors, radius=1.2, textprops={'fontsize': 6, 'font': 'lato'})

    if shade != 0:
        middle_color = "#ebebea"
    else:
        middle_color = "white"
    
    my_circle = plt.Circle( (0,0), 0.8, color=middle_color)
    p = plt.gcf()
    p.set_size_inches(2.4,1.3)
    p.gca().add_artist(my_circle)
    plt.savefig(f'{TEMPLATES_DIR}/tmp/{chart}.png', transparent=True)

    logging.debug('Saved new pie chart: {}.png'.format(chart))

def save_pdf(html):
    options = {
        'page-size': 'Letter',
        'margin-top': '23',
        'margin-right': '0',
        'margin-bottom': '20',
        'margin-left': '0',
        'encoding': "UTF-8",
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ],
        'allow': ["templates"],
        'enable-local-file-access': None,
        'enable-internal-links': None,
        'keep-relative-links': None,
        'footer-html': "templates/footer.html",
        'header-html': "templates/header.html",
    }

    if not os.path.exists('reports'):
        os.makedirs('reports')
        logging.warning('Reports dir did not exist, it has been created')    

    pdfkit.from_string(html, 'reports/{}-report.pdf'.format(FILE_DATE), options=options, css="templates/report.css")


def main(zone, policies, secure_url, secure_token):

    # Gather initial results 
    logging.info("Retrieveing policy results from Sysdig Console.")
    cspm_filter = policy_filter(zone, policies, page_size=1000)
    report = get_report(secure_url, secure_token, cspm_filter)

    # Put report into a format easier to work with
    report = convert_report(report)
    logging.info("convert report complete")

    #Load and process templates
    logging.info("Processing templates")
    report_template = load_templates()
    finished_template = template(report_template, data=report, zone=options.zone, base_url=secure_url, templates_dir=TEMPLATES_DIR, date=DATE_PRETTY)
    report_html = markdown2.markdown(finished_template, extras={"tables": None, "markdown-in-html": None, "header-ids": None})

    # Create pie charts, previous charts are overwritten
    make_charts(report)

    # Generate our report, it overwrites any previously created reports 
    logging.info("Generating PDF")
    save_pdf(report_html)
    logging.info("Report generation complete")




if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option(
        "-z", "--zone",
        dest="zone",
        default="Entire Infrastructure",
        help="limit report results to a specific zone")

    parser.add_option(
        "-p", "--policy",
        dest="policy", 
        help='specific policy, or list of policies to create report for - if more than one policy, use the format "<policy name1>, <policy name2>, ..."')

    parser.add_option("-s", "--secure-url",
        dest="secure_url",
        default=SDC_SECURE_URL,
        help="Sysdig Secure Console base URL")

    parser.add_option("-t", "--token",
        dest="token",
        default=SDC_SECURE_TOKEN,
        help="Sysdig Secure API Token")
    
    parser.add_option("-l", "--logging",
        dest="logging",
        default="INFO",
        help="Set logging level for report generator")

    #future?    
    #parser.add_option("-r", "--requirement-details", dest="detailed_requirements", default=None, help="Requirements, by ID, to include detailed output for when detailed output is anbled with '-d'", nargs="+", type=int)
    #parser.add_option("-d", "--detailed", dest="detailed", default=False, action="store_true", help="Include detailed output for one or more requirements")

    (options, args) = parser.parse_args()

    # Check for API Token, utilize env var if possible
    if options.token is None:
        print("Please provide a Sysdig Secure API token.")
        sys.exit(1)
  

    # Check for Secure URL, utilize env var if possible
    if options.secure_url is None:
        print("Please provide the base URL for your Sysdig Secure Console.")
        sys.exit(1)

    try:
        logging.basicConfig(level=options.logging)
    except ValueError:
        print("Logging level must be one of [DEBUG, INFO, WARNING, ERROR, CRITICAL]")
        sys.exit(1)

    plt.set_loglevel("info")

    main(options.zone, options.policy, options.secure_url, options.token)