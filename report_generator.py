from optparse import OptionParser
import http.client
import os
import urllib.parse

parser = OptionParser()

parser.add_option("-z", "--zone", dest="zone", default="Entire Infrastructure", help="limit report results to a specific zone")
parser.add_option("-p", "--policy", dest="policy", help="specific policy to create report for")
parser.add_option("-s", "--secure-url", dest="secure_url", help="Sysdig Secure Console base URL")
parser.add_option("-k", "--key", dest="key", help="Sysdig Secure API Key")

(options, args) = parser.parse_args()

# Check for API Key, utilize env var if possible
if options.key is None:
    secure_api_key = os.environ.get('SDC_SECURE_TOKEN')
    if secure_api_key is None:
        print("Please provide a Sysdig Secure API key.")
        sys.exit(1)
else:
    secure_api_key = options.key

# Check for Secure URL, utilize env var if possible
if option.secure_url is None:
    secure_base_url = os.environ.get('SDC_SECURE_URL')
    if secure_base_url is None:
        print("Please provide the base URL for your Sysdig Secure Console.")
        sys.exit(1)
else:
    secure_base_url = options.secure_base_url

def policy_filter():
    request_filter = f'filter=zone.name="{options.zone}"'
    if options.policy:
        request_filter = f'{request_filter} and policy.name="{options.policy}"'
    return request_filter


def getReport(filter=""):
    conn = http.clientHTTPSConnection(secure_base_url)

    escaped_filter = urllib.parse.quote(filter)

    conn.request("GET", f"/api/cspm/v1/compliance/requirements{}")
    res = conn.getresponse()
    data = res.read()

    return data


