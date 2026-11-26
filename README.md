# Inventário Cycat — Gestão de Ativos e Análise de Risco

Segunda atividade avaliativa (Sprints 3, 4 e 5) do curso de Bacharelado em
Cibersegurança da Universidade Federal de Uberlândia (UFU) — período
letivo 2026/2.

---

## O que o programa faz

Cadastra equipamentos de TI (ativos), registra as vulnerabilidades
associadas a cada um e calcula o risco de cada ativo usando um modelo
linear que leva em conta as vulnerabilidades próprias, o tipo do
equipamento e as dependências entre ativos da rede.

Evolui a primeira atividade avaliativa reescrevendo toda a aplicação no
paradigma de orientação a objetos, roda em container Docker e inclui uma
interface gráfica opcional além da linha de comando original.

---

## Como executar

### Opção 1 — Linha de comando (menu textual)

Requer Python 3.11 ou superior.

```bash
pip install -r requirements.txt
python main.py
```

### Opção 2 — Interface gráfica (CustomTkinter)

```bash
pip install -r requirements.txt
python interface_grafica.py
```

Credenciais de teste da interface gráfica:
- **Admin:** usuário `admin`, senha `admin` — cadastra, edita e exclui.
- **Analista:** usuário `analista`, senha `analista` — visualiza e
  atualiza status, com permissões restritas.

### Opção 3 — Container Docker (modo servidor)

```bash
sudo docker compose up -d --build
sudo docker compose ps        # confirme que aparece "(healthy)"
sudo docker compose logs --tail 20
```

No modo servidor o programa não abre menu: inicia um laço de batimento
("heartbeat") que registra no log, a cada dez segundos, uma linha
confirmando que a aplicação está viva.

---

## Estrutura do projeto

```
.
├── main.py                 Menu textual (CLI) e modo servidor para o Docker
├── interface_grafica.py    Entrada da interface gráfica (opcional)
├── modelos.py              Classes de domínio: Equipamento (ABC) + subclasses,
│                           Vulnerabilidade, Dependencia
├── enums.py                Tipos: TipoAtivo, Severidade, StatusTratamento
├── inventario.py           Regras de negócio e orquestração (CRUD)
├── persistencia.py         Leitura e gravação atômica do JSON
├── analise_risco.py        Modelo linear: monta M, v, W, A e resolve (I-A)x = b
├── catalogo.py             Integração opcional com o NVD (busca por CVE ou tipo)
├── interface/              Telas da interface gráfica
├── assets/cycat/           Mascote do sistema
├── tests/                  Testes automatizados (unittest)
├── dados/                  Base de dados em JSON (gerada em tempo de execução)
├── Dockerfile              Imagem Python 3.11-slim com HEALTHCHECK
├── compose.yaml            Orquestração do container com volume persistente
└── requirements.txt        numpy, requests, deep-translator, customtkinter, Pillow
```

As camadas estão separadas (domínio → persistência → regras →
apresentação), preparando a aplicação para ser reescrita como backend web
no próximo trabalho.

---

## Modelo de análise de risco

Para `n` equipamentos e `m` vulnerabilidades distintas, o programa monta:

- **M** (n × m) — matriz de incidência. `M[i][j] = 1` se o equipamento
  `i` é afetado pela vulnerabilidade `j` e ela não está corrigida; caso
  contrário, `M[i][j] = 0`.
- **v** (m) — vetor de severidade (nota CVSS de cada vulnerabilidade).
- **W** (n × n) — matriz diagonal de exposição. `W[i][i] = 1 + fator(i)`,
  onde o fator depende do tipo do equipamento (polimorfismo).
- **b** (n) — risco próprio: `b = W · M · v`.
- **A** (n × n) — matriz de dependências. `A[i][j]` é a fração do risco
  do equipamento `j` herdada por `i` (com `A[i][i] = 0`).
- **x** (n) — risco efetivo: solução de `(I − A) · x = b`.

### Como a invertibilidade é verificada

Antes de resolver o sistema, o programa aplica dois critérios em ordem:

1. **Dominância diagonal estrita** — se a soma de cada linha de `A` for
   menor que 1, `I − A` é estritamente diagonal dominante e, portanto,
   invertível. Essa é uma condição suficiente. O cadastro de dependências
   impõe essa regra, garantindo invertibilidade por construção.
2. **Número de condição** — se não houver dominância, o programa
   verifica se o número de condição de `I − A` é finito e abaixo de
   `1e12`. Acima disso, a matriz é singular ou muito próxima disso, e o
   programa avisa o usuário em vez de devolver um resultado não
   confiável.

O determinante é exibido só como informação, porque seu valor muda com a
escala da matriz e não serve como critério isolado.

### Por que `solve` e não `inv`

O código resolve `(I − A) · x = b` com `numpy.linalg.solve`, que usa
fatoração LU. Isso é mais preciso e mais barato do que calcular
`numpy.linalg.inv(I − A)` e multiplicar por `b`, especialmente quando a
matriz é mal condicionada.

---

## Persistência

Os ativos são gravados em `dados/inventario_ativos.json` como um array
(lista) de objetos JSON. As dependências ficam em
`dados/dependencias_rede.json`, no mesmo formato.

A gravação é **atômica**: o programa escreve num arquivo temporário e
troca o arquivo original com `os.replace`. Se o programa cair no meio da
escrita, o arquivo anterior continua intacto. Se o arquivo for aberto e
estiver corrompido, ele é renomeado com sufixo `.corrompido-{timestamp}`
em vez de ser sobrescrito, preservando os dados para análise posterior.

---

## Container Docker

- **Imagem base:** `python:3.11-slim`.
- **Modo servidor:** o `CMD` padrão roda `python main.py servidor`, que
  dispara o laço de batimento sem menu interativo.
- **Volume persistente:** `./dados:/app/dados` garante que os ativos
  sobrevivam a reinícios do container.
- **Reinício automático:** `restart: unless-stopped` recoloca o
  container no ar se o processo crashar, se o Docker reiniciar, ou se o
  servidor rebootar.
- **HEALTHCHECK com arquivo de batimento:** a cada dez segundos, o modo
  servidor grava a hora atual em `/tmp/heartbeat.txt`. A cada trinta
  segundos, o HEALTHCHECK verifica se esse arquivo foi atualizado nos
  últimos sessenta segundos. Se não foi, o container é marcado como
  `unhealthy` em `docker ps`. Isso detecta deadlock, não só crash.

---

## Perfis e permissões (interface gráfica)

- **Admin** — cadastra, edita e remove ativos; cadastra, atualiza status
  e remove vulnerabilidades; cadastra e remove dependências.
- **Analista** — visualiza ativos e dependências; cadastra
  vulnerabilidades e atualiza o status delas, mas não pode remover; não
  pode alterar dependências.

---

## Integração opcional com o NVD

As vulnerabilidades podem ser importadas direto do National Vulnerability
Database (NVD) do NIST, de duas formas:

- **Por CVE específico** — digita o identificador (ex.: `CVE-2021-44228`)
  e o programa busca descrição, CVSS, severidade e categoria (CWE)
  diretamente da API oficial.
- **Por tipo de vulnerabilidade** — oito categorias comuns em português
  (Injeção de SQL, Cross-Site Scripting, Credenciais fracas, etc.) ou
  termo livre em inglês. As descrições são traduzidas em paralelo para
  português via MyMemory Translator.

---

## Testes automatizados

```bash
python -m unittest -v
```

O arquivo `tests/test_analise_risco.py` inclui um cenário resolvido à
mão (três equipamentos, duas dependências) cujos resultados são
conferidos contra a implementação — exatamente a "validação com cenário
pequeno" que o enunciado sugere na seção de dicas.

---

## Dependências

Declaradas em `requirements.txt`:

- `numpy` — álgebra linear (matrizes, determinante, número de condição,
  resolução de sistemas lineares).
- `requests` — consulta à API do NVD.
- `deep-translator` — tradução das descrições CVE para português.
- `customtkinter` — interface gráfica.
- `Pillow` — carregamento das imagens da mascote.

---

## Observações finais

O programa foi desenhado para também servir de **precursor** da
aplicação web prevista para a próxima etapa, conforme o enunciado
antecipa. A separação em camadas (domínio → persistência → regras →
apresentação) permite trocar a camada de apresentação por um framework
web (Flask, FastAPI) sem alterar as regras de negócio nem o modelo de
análise de risco.