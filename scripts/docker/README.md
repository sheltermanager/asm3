# Docker Development Environment

Development environment for ASM3 with Docker. This stack creates two containers:

- **postgres**: Simple postgres database
  - user: asm3
  - pass: asm3
  - db: asm
- **asm**: ASM3 application running in container. Configurations defined in [asm3.conf.dev](./asm3.conf.dev)

## Get Started

### Containers Up

```bash
docker-compose build
docker-compose up -d
```

Open [http://localhost:5000](http://localhost:8080) to view the running application

### Containers Down

```bash
docker-compose down -v
```

## Future

- Create a base docker image to replace `ubuntu:latest` with all dependenies pre-installed
