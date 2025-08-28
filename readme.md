# Clarifica 📖✨

Um reformatador inteligente de PDFs para uma leitura perfeita em qualquer tela.

---

## O Problema

Muitos documentos PDF, especialmente livros e artigos antigos, possuem um layout fixo pensado para impressão. A leitura desses arquivos em telas pequenas, como celulares e e-readers, é uma experiência frustrante, com quebras de linha ruins, fontes pequenas e elementos de layout que poluem o conteúdo.

Este projeto nasceu da necessidade de ler o livro "Puer Aeternus" em português, cuja versão em PDF era mal formatada para dispositivos móveis.

## A Solução

O **Clarifica** é um pipeline em Python que analisa a estrutura de um PDF, descarta o "ruído" do layout e reconstrói o conteúdo em um novo documento limpo, fluido e padronizado em A4, ideal para leitura digital.



---

## Principais Funcionalidades

* **Análise Heurística:** O sistema primeiro lê o documento inteiro para aprender sobre sua estrutura, identificando a fonte principal e elementos de layout que se repetem.
* **Limpeza Inteligente:** Remove automaticamente cabeçalhos, rodapés, números de página e bordas decorativas que se repetem ao longo do documento.
* **Preservação de Hierarquia:** Identifica e mantém a estrutura de títulos, subtítulos e parágrafos com base na análise tipográfica.
* **Tratamento de Imagens:** Extrai, posiciona e redimensiona corretamente as imagens que fazem parte do conteúdo.
* **Padronização:** Gera um arquivo de saída limpo, sempre em formato A4, com fontes legíveis e um layout de fluxo contínuo.

## Tecnologias Utilizadas

* **Python 3.11+**
* **PyMuPDF (Fitz):** Para a extração e análise de baixo nível dos dados do PDF.
* **ReportLab:** Para a criação e geração do novo documento PDF.
* **Poetry:** Para gerenciamento de dependências e do ambiente virtual.

---

## Arquitetura do Projeto

O Clarifica utiliza uma arquitetura em três fases para garantir um resultado robusto e previsível:

1.  🧠 **Análise (`analyzer.py`):** O "cérebro" do projeto. Lê o documento inteiro para criar um "mapa" com a fonte principal e uma "lista negra" de elementos de layout repetitivos.
2.  🏗️ **Construção (`builder.py`):** O "arquiteto". Percorre o documento uma segunda vez, usando o mapa para filtrar o ruído e construir uma `story` limpa e estruturada de conteúdo com objetos do ReportLab.
3.  📄 **Geração (`generator.py`):** O "construtor". Pega a `story` pronta e a renderiza em um novo arquivo PDF limpo e formatado.

---

## Como Usar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/clarifica.git](https://github.com/SEU_USUARIO/clarifica.git)
    cd clarifica
    ```

2.  **Instale as dependências com o Poetry:**
    ```bash
    poetry install
    ```

3.  **Adicione seu PDF:**
    Coloque o arquivo PDF que você deseja reformatar dentro da pasta `input_docs/`.

4.  **Configure o arquivo de entrada:**
    Abra o arquivo `clarifica/main.py` e atualize a variável `FILE_NAME` com o nome do seu PDF.
    ```python
    # clarifica/main.py
    FILE_NAME = "seu_livro.pdf"
    ```

5.  **Execute o projeto:**
    ```bash
    poetry run python -m clarifica.main
    ```

6.  **Encontre o resultado:**
    Seu novo PDF, limpo e reformatado, estará na pasta `output_docs/`.

---

## Próximos Passos (Roadmap)

- [ ] Implementar a fusão inteligente de blocos de texto para títulos que foram quebrados em múltiplas linhas.
- [ ] Adicionar detecção de caracteres sobrescritos (superscript) para preservar formatações
- [ ] Criar uma interface de linha de comando (CLI) mais amigável para não precisar editar o código para trocar de arquivo.

---

## Licença

Este projeto está sob a licença MIT.
