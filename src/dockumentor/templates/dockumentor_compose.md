# 🐳 Docker Compose Architecture

This documentation was automatically generated to map out the services, networks, and dependencies defined in the infrastructure.

## 🏗️ System Overview

### Architecture Flowchart
```mermaid
{{ mermaid_flowchart }}
```

### Service Initialization Sequence
```mermaid
{{ mermaid_sequence }}
```

---

## 📦 Services Specification

{% for name, service in services.items() %}
### {{ name }}
🐳 {{ service.image }}

command: `{{ service.command }}`

| Configuration | Details |
|--------------|---------|
| **Networks** | {{ service.networks | join(', ') | default('default', true) }} |
| **Dependencies** | {{ service.depends_on | join(', ') | default('None', true) }} |

{% if service.ports %}
**Exposed Ports:**
{% for port in service.ports %}* `{{ port }}`
{% endfor %}
{% endif %}

{% if service.environment %}
**Environment Variables:**
```env
{% for key, val in service.environment.items() %}{{ key }}={{ val }}
{% endfor %}```
{% endif %}

{% if service.volumes %}
**Volumes:**
{% for vol in service.volumes %}* `{{ vol }}`
{% endfor %}
{% endif %}

---
{% endfor %}

## 🌐 Network Flow Analysis

```mermaid
{{ mermaid_sankey }}
```

## 🛠️ Operations & Quick Start

```bash
# Start all services in the background
{{ example_commands.start }}

# View real-time logs for a specific service
{{ example_commands.logs }}

# Shut down and remove containers/networks
{{ example_commands.stop }}
```
