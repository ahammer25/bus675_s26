# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below

## Lab 2 Reflection

If these containers were running in separate datacenters, the setup would be more complex than what I did for this lab. The preprocessor would not be able to use `host.docker.internal` anymore, because the inference API would no longer be running on the same host machine. Instead, the preprocessor would need to send requests to a real network address, like a public or private DNS name, load balancer address, or service endpoint for the inference API. The `docker run` command for the preprocessor would still include an `API_URL` environment variable, but it would point to that remote API address instead of a local host-based one.

The shared volume setup would also be different. On my laptop, I could mount local `incoming/` and `logs/` folders directly into the containers, but that would not work across different datacenters. Instead, the system would need shared remote storage, like cloud object storage, a database, or some kind of message queue so both services could access the data they need. Running services in separate datacenters would also create new challenges like network latency, connection failures, authentication, encryption, retries, monitoring, and making sure the system can recover if one side goes down. So overall, the architecture would move from a simple local container setup to a more distributed system with real networking and infrastructure concerns.