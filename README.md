# FPQ - Formato Padrão de Questionários

O Formato Padrão de Questionários é uma linguagem baseada na sintaxe YAML para especificar questionários.

## Formato

Existem dois tipos de arquivo: o de respostas padronizadas, obrigatoriamente chamado `respostas.yaml`, e o dos questionários

### Regras da sintaxe YAML

Resumidamente, a sintaxe YAML tem dois tipos de entidade: a chave e o valor. O valor de uma dada chave pode ser outra chave, representando assim uma estrutura hierárquica. O valor também pode ser uma string de texto ou uma lista, indicada por colchetes

    [a,b,c]
    
ou, alternativamente, em linhas separadas

  - a
  - b
  - c

 A documentação completa pode ser conferida em [yaml.org](yaml.org). Cabe lembrar, contudo, que nem tudo o que é YAML válido funciona como código FPQ.
 
### Formato do arquivo de respostas

O arquivo de respostas é uma lista hierárquica da seguinte forma:

    tipo-resposta1:
        conjunto1: 
          - opção
          - opção
          - opção
        conjunto 2:
           - discordo
           - concordo
    tipo-resposta2:
        conjunto3: 
          - opção
          - opção
          - opção

Os tipos de resposta a que o conversor para Word suporte são:

* `likert` (escala ascendente)
* `escolha única`
* `escolha múltipla`
* `relevância` (escolha única onde o primeiro item é do tipo "não é relevante")
* `composição`
* `valor`
* `talvez valor` (Escolha única onde a última inclui um campo de valor
* `lista`

### Formato de arquivo de questionário

Cada questionário tem três partes: `conteúdo`, `seções` e `questões`. 

A primeira parte tem a seguinte forma:


    conteúdo:
      título: Políticas de Exemplo
      seções: 
        - seção1
        - seção2
        - seção3


As seções são definidas na parte seguinte:


    seções:
      seção1:
        título: Primeira Seção
        conteúdo:
          - q1
          - q2
          - q3
      seção2:
        título: Segunda Seção
        conteúdo:
          - q4
          - q5
          - q6
      seção3:
        título: Terceira Seção
        conteúdo:
          - p*


O conteúdo das seções são questões definidas na parte seguinte (sendo que acima a terceira seção tem todas as questões que começam com `p`. A parte das questões tem o seguinte formato:


    questões:
      q1:
        texto: Este exemplo é bom para que problemas?
        tipo-resposta: escolha múltipla
        respostas:
          - Problemas tipo 1
          - Problemas tipo 2
     q2:
      texto: Este exemplo serve para algo?
      respostas:
          - Sim
          - Não
     q3:
      texto: Quantos exemplos são necessários?
      tipo-resposta: valor 
     q4:
      ascendentes: [q3]
      texto: Quantos exemplos de cada tipo faltam?
      tipo-resposta: valor
      respostas:
        - Exemplos específicos
        - Exemplos gerais
     q5: 
      texto: |
          Finalmente: este caractere ":" só pode ser usado em um texto multilinha assim.
      respostas:
        - Não sabia
        - Óbvio.


No modelo acima observamos as seguintes regras:

* Uma questão deve ter um campo `texto` e (ou um campo `tipo-resposta` ou um campo `respostas`). 
* Caso não exista um `tipo-resposta`, presume-se que seja `escolha única`. 
* Caso não exista um valor, presume-se que só exista uma opção sem texto.
* A questão `q4` virá sempre precedida da questão `q3`, mesmo que esqueçamos de incluí-la em uma seção.

Finalmente, questões que não foram incluídas em nenhuma seção aparecerão em uma seção chamada "Outros"

## Instalação da ferramenta de conversão para Word

Para usar a ferramenta de conversão é necessário:

* Ambiente Python. Uma versão fácil de instalar é o [Anaconda](https://www.anaconda.com/download/) (disponível inclusive nos computadores da biblioteca da FGV)
* Baixar `fpq.py` e `fpq2docx.py`
* (Opcional, recomendado) Criar um ambiente Python digitando `python -m venv fpq && source fpq/bin/activate`
* Criar um arquivo de respostas chamado `respostas.yaml` e um documento Word vazio chamado `template.docx`

Para usar a ferramente basta digitar

    python fpq2docx.py meu_questionario.yaml
