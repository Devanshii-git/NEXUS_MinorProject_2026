# Dataset Summary

- Total samples: 5905
- Source groups: {'custom_generated': 4993, 'formal_fr': 100, 'pure_fr': 546, 'formal_nfr': 100, 'pure_nfr': 166}
- Label distribution: {'ACTOR': 5354, 'ACTION': 5905, 'FEATURE': 5892, 'CONSTRAINT': 5175, 'QUALITY': 5032, 'PRIORITY': 4993}
- Average entities per sample: 5.479
- Samples with 3+ entities: 5394
- Samples with PRIORITY labels: 4993
- Cross-label phrase conflicts: 9

## Example Samples

- Text: Quick msg: not sure why this keeps happening. admin needs to process the notifications service under heavy load. Also make sure it is responsive. This is high priority.
  Entities: [('admin', 'ACTOR'), ('process', 'ACTION'), ('notifications service', 'FEATURE'), ('under heavy load', 'CONSTRAINT'), ('responsive', 'QUALITY'), ('high priority', 'PRIORITY')]
- Text: Teams chat: backend service needs to monitor the notifications service every day. Also make sure it is robust. This is P1.
  Entities: [('backend service', 'ACTOR'), ('monitor', 'ACTION'), ('notifications service', 'FEATURE'), ('every day', 'CONSTRAINT'), ('robust', 'QUALITY'), ('P1', 'PRIORITY')]
- Text: Meeting note: not sure why this keeps happening. QA team needs to handle the search feature before next release. Also make sure it is responsive. This is ASAP.
  Entities: [('QA team', 'ACTOR'), ('handle', 'ACTION'), ('search feature', 'FEATURE'), ('before next release', 'CONSTRAINT'), ('responsive', 'QUALITY'), ('ASAP', 'PRIORITY')]
- Text: Email: client needs to deploy the payment gateway within SLA. Also make sure it is fast. This is high priority.
  Entities: [('client', 'ACTOR'), ('deploy', 'ACTION'), ('payment gateway', 'FEATURE'), ('within SLA', 'CONSTRAINT'), ('fast', 'QUALITY'), ('high priority', 'PRIORITY')]
- Text: Meeting note: users are complaining. frontend app needs to generate the dashboard under heavy load. Also make sure it is scalable. This is high priority.
  Entities: [('frontend app', 'ACTOR'), ('generate', 'ACTION'), ('dashboard', 'FEATURE'), ('under heavy load', 'CONSTRAINT'), ('scalable', 'QUALITY'), ('high priority', 'PRIORITY')]
- Text: Jira ticket: might be related. backend service needs to log the API before next release. Also make sure it is efficient. This is high priority.
  Entities: [('backend service', 'ACTOR'), ('log', 'ACTION'), ('API', 'FEATURE'), ('before next release', 'CONSTRAINT'), ('efficient', 'QUALITY'), ('high priority', 'PRIORITY')]
- Text: Teams chat: user needs to optimize the payment gateway after login. Also make sure it is robust. This is P1.
  Entities: [('user', 'ACTOR'), ('optimize', 'ACTION'), ('payment gateway', 'FEATURE'), ('after login', 'CONSTRAINT'), ('robust', 'QUALITY'), ('P1', 'PRIORITY')]
- Text: Slack thread: btw this came up again. QA team needs to deploy the database under heavy load. Also make sure it is robust. This is P0.
  Entities: [('QA team', 'ACTOR'), ('deploy', 'ACTION'), ('database', 'FEATURE'), ('under heavy load', 'CONSTRAINT'), ('robust', 'QUALITY'), ('P0', 'PRIORITY')]
- Text: Quick msg: not sure why this keeps happening. QA team needs to retry the reports module under heavy load. Also make sure it is available. This is high priority.
  Entities: [('QA team', 'ACTOR'), ('retry', 'ACTION'), ('reports module', 'FEATURE'), ('under heavy load', 'CONSTRAINT'), ('available', 'QUALITY'), ('high priority', 'PRIORITY')]
- Text: Teams chat: might be related. client needs to handle the reports module in real time. Also make sure it is responsive. This is urgent.
  Entities: [('client', 'ACTOR'), ('handle', 'ACTION'), ('reports module', 'FEATURE'), ('in real time', 'CONSTRAINT'), ('responsive', 'QUALITY'), ('urgent', 'PRIORITY')]