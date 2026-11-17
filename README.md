# VetCare

Sistema web de gestão para clínica veterinária, desenvolvido como projeto
acadêmico em Python com Flask, SQLAlchemy e SQLite.

## Como rodar

Abra a pasta do projeto no VS Code e, no terminal integrado (Ctrl + '):

```
python -m pip install -r requirements.txt
python seed.py
python app.py
```

Depois acesse **http://127.0.0.1:5000** no navegador.

O `seed.py` só precisa ser rodado uma vez: ele cria o arquivo `vetcare.db`
com as tabelas e um conjunto de dados de demonstração. Para recomeçar do
zero, apague o `vetcare.db` e rode o `seed.py` de novo.

> Se o comando `pip` não for reconhecido, use sempre `python -m pip`.

## Contas de teste

Todas usam a senha `123456`.

| E-mail | Perfil |
| --- | --- |
| admin@vetcare.vet | Administrador |
| helena@vetcare.vet | Veterinária |
| rafael@vetcare.vet | Veterinário |
| recepcao@vetcare.vet | Recepção |

## Perfis de acesso

| | Administrador | Veterinário | Recepção |
| --- | --- | --- | --- |
| Tutores e animais | tudo | consulta | tudo |
| Agenda | todas | só as próprias consultas | todas |
| Prontuário e receita | tudo | só os próprios pacientes | sem acesso |
| Vacinação | tudo | registra | consulta |
| Pagamentos e serviços | tudo | sem acesso | lança e dá baixa |
| Usuários | tudo | sem acesso | sem acesso |

A permissão é verificada na rota, pelo decorador `@exige()` em `security.py`.
Esconder o botão no HTML não é suficiente: digitar a URL direto também cai na
verificação e devolve a página de erro 403.

## Organização dos arquivos

```
vetcare/
├── app.py              fábrica da aplicação, filtros e tratamento de erros
├── extensions.py       instância do SQLAlchemy
├── models.py           as 14 tabelas do sistema
├── security.py         sessão, decorador @exige() e regras por perfil
├── seed.py             cria o banco e popula com dados de teste
├── requirements.txt
├── blueprints/
│   ├── auth.py         login e saída
│   ├── painel.py       tela inicial
│   ├── cadastros.py    tutores, animais e veterinários
│   ├── agenda.py       marcação de consultas
│   ├── clinico.py      prontuário, receita e vacinação
│   ├── financeiro.py   serviços e pagamentos
│   └── admin.py        usuários e catálogo de vacinas
├── templates/
└── static/css/
```

## Modelo de dados

São 14 tabelas:

**Acesso** — `usuarios`, `veterinarios`
**Cadastros** — `tutores`, `animais`, `especies`, `racas`
**Clínico** — `agendamentos`, `prontuarios`, `receitas`, `itens_receita`,
`vacinas`, `aplicacoes_vacina`
**Financeiro** — `servicos`, `pagamentos`

## Para rodar em grupo

O banco (`vetcare.db`) não vai junto no repositório, de propósito: cada
integrante roda o `seed.py` e gera o seu. Assim ninguém sobrescreve os dados
de teste do outro ao dar commit.

Para acessar de outro computador da mesma rede, troque a última linha do
`app.py` por `app.run(debug=True, host="0.0.0.0")` e use o IP da máquina no
lugar de 127.0.0.1.
