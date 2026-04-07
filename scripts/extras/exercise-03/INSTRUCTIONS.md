# Exercise 0x03 - Dynamic Context

## Objective
Utilize raw dynamic data to craft context about an application. Ignore code to see what can be observed from web interactions with an application.

## Instructions
### 1. Run Script
Open _exercise-03/dynamic\_context.py_ and view both the `system_prompt_template` and `user_question` variables. The overall structure of the script is similar to reviewing code. The results of these queries will be limited to the number of application interactions, but we can still learn a lot from even small interactions.

Run the script multiple times to view the current state of interactions. Note the differences.
```sh
python scripts/exercise-03/dynamic_context.py
```

Observe the output based on the current context contained in the vector database.

### 2. Review Current Context
The current context is limited to the HTTP Sessions contained in the _data/vtm-session.xml_ file, that has been vectorized for retrieval. Open this file and note the number of HTTP Requests and Responses and types of interactions recorded. Even limited to the URLs there is enough to start building out a knowledgebase of how the application performs.

```xml
<item>
    <time>Tue Aug 05 17:43:43 MDT 2025</time>
    <url><![CDATA[https://vtm.rdpt.dev/]]></url>
    <host ip="50.112.153.244">vtm.rdpt.dev</host>
    <port>443</port>
    <protocol>https</protocol>
    <method><![CDATA[GET]]></method>
    <path><![CDATA[/]]></path>
    <extension>null</extension>
    <request base64="true">...</request>
    <status>302</status>
    <responselength>433</responselength>
    <mimetype></mimetype>
    <response base64="true">...</response>
    <comment></comment>
  </item>
  <item>
    <time>Tue Aug 05 17:44:23 MDT 2025</time>
    <url><![CDATA[https://vtm.rdpt.dev/static/taskManager/js/backend/common-scripts.js]]></url>
    <host ip="50.112.153.244">vtm.rdpt.dev</host>
    <port>443</port>
    <protocol>https</protocol>
    <method><![CDATA[GET]]></method>
    <path><![CDATA[/static/taskManager/js/backend/common-scripts.js]]></path>
    <extension>js</extension>
    <request base64="true">...</request>
    <status>200</status>
    <responselength>4230</responselength>
    <mimetype>script</mimetype>
    <response base64="true">...</response>
    <comment></comment>
  </item>
```

Given the current prompt, there is room for improvement as the original developers are asking the LLM to make broad analysis along a number of different paths, including authentication, authorization, and various component identifications.

```py
question = """"
Please analyze the full HTTP Session a comprehensive assessment of the application by addressing the following:

- Purpose of the application
- Web technologies used in the application
- Templating language used in the application
- Database used in the application
- Authentication mechanisms used in the application
- Authorization mechanisms used in the application
- Server software and versions
- Frameworks and libraries used, including their versions

Analyze each request in the session until all requests have been analyzed.
"""
```

### 3. Improve Context
Now it's your turn to improve the quality of the results by modifying the above prompt. Utilize a prompt engineering framework or reflection combined with focused tasks to achieve these results.

Specifically, improve the `question` by focusing the AI's attention on 1-2 specific tasks with consistent output format. Utilize the example in _prompts/2-authentication.txt_ to build context for authorization endpoints, input validation, and any other interesting security features that can be gleaned from the current session.

