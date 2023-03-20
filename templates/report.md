<div id="title" markdown="1">
# Sysdig Posture Compliance Report

![]({{ templates_dir }}/title-break.png)

Generated on {{date}}
</div>
## Overview

Compliance results for Policies in the "**{{ zone }}**" zone.

<div id="policies" markdown="1">
This Report contains results for the following policies:

% for policy in data.keys():
- [{{policy}}](#summary-results-for-policy-{{data[policy]['normalizedName']}})
% end
</div>

% for policy in data.keys():
## Summary Results for Policy: {{ policy }}

![]({{ templates_dir }}/tmp/pol-{{ data[policy]['policyId'] }}.png)

This Policy has {{len(data[policy]['pass']) + len(data[policy]['fail'])}} requirements currently being evaluated.

Overall, this policy is passing  **{{ int(100 * len(data[policy]['pass']) / (len(data[policy]['pass']) + len(data[policy]['fail']))) }}%** of the included requirements.  

    % if len(data[policy]['pass']) > 0:
<div id="success" markdown="1">

### Passing Requirements
| Requirement | Severity |
|:------------|:---------|
        % for req in data[policy]['pass']:
| {{req['name']}} | **{{req['severity']}}** |
        % end
</div>
    % else:
**This Policy does not currently have any passing requirements, please see failure summary below.**
    % end


### Failing Requirements


This section provides a summary of failed requirements for the  **{{policy}}** policy. The requirements are prioritized in order
of most failed resources for the highest severity. The general severity for the requirement matches highest control severity for
which there is a failure. More detail for the policy or controls can be viewed in the Sysdig Secure console.

    % failure_count = 0
    % for req in data[policy]['fail']:
<div id="failures" class="fail{{failure_count % 2}}" markdown="1">

#### {{ req['name'] }}

![]({{ templates_dir }}/tmp/req-{{ req['requirementId'] }}.png)

This requirement has an overall severity of  **{{req['severity']}}**.

This Requirement is failing {{int(100 * req['failedControls']/len(req['controls']))}}% of controls.  
There is a total of  **{{req['failedControls']}}** failed controls out of  **{{len(req['controls'])}}**.

##### Failing Resources by Control Severity
| High | Medium | Low |
|:-------|:----|:--------------|
| {{req['highSeverityCount']}} | {{req['mediumSeverityCount']}} | {{req['lowSeverityCount']}} | 

There is a total of  **{{req['acceptedCount']}}** resources with _Accepted Risks_ for controls in this requirement.
###### Requirement ID: {{req['requirementId']}} - [View In Sysdig Console](https://{{base_url}}/#/compliance/views/results?filter=zone.name = "{{zone}}" and policy.name = "{{policy}}" and name in ("{{req['name']}}"))
</div>
        % failure_count += 1
    % end
---
% end