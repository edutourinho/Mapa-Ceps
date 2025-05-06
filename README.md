# Mapa-Ceps
Mapa de Ocorrências por CEP (TRT-1)
Web-app em Streamlit que:

Carrega um CSV com CEP, ocorrências, lat, lon e OJ

Plota cada CEP em um mapa Folium, usando cores distintas por OJ

Permite desenhar retângulo ou polígono para filtrar pontos

Mostra — em tempo real — total de CEPs e ocorrências dentro da área

Exporta um CSV apenas com os CEPs selecionados

Exibe totais globais por OJ na sidebar

Segue a identidade visual do TRT-1
1. Estrutura
2. app.py
requirements.txt
static/
└─ logo_trt1_horizontal.png
.streamlit/
└─ config.toml
2. Requisitos
Pacote	Versão testada
streamlit	1.45
streamlit-folium	0.25
folium	0.14
pandas, numpy	atuais
shapely	≥ 2.0
matplotlib	≥ 3.8
3. Formato do CSV
4. | cep      | ocorrencias | lat      | lon      | oj        |
| -------- | ----------- | -------- | -------- | --------- |
| 21010010 | 5           | -22.8934 | -43.1883 | OJ Centro |
| 22770090 | 12          | -23.0123 | -43.3188 | OJ Barra  |
cep: string de 8 dígitos (sem “-”)

lat / lon: WGS-84 (graus decimais)

oj: nome livre do Oficial de Justiça
4. Uso
Clique em “Browse files” (sidebar) e envie o cep.csv.

O mapa carrega com círculos coloridos por OJ.

Escolha Retângulo ou Polígono, desenhe a área de interesse.

Veja na sidebar:

Totais globais por OJ (tabela)

CEPs e ocorrências dentro da área

Botão ⬇️ Baixar CSV dos pontos filtrados

Redesenhe quantas vezes quiser — os números se atualizam na hora.

5. Deploy no Streamlit Cloud
Fork ou clone o repositório.

No site share.streamlit.io → New app

Repo: SEU-USUARIO/SEU-REPO

Branch: main

File: app.py

Deploy. Em ~2 min o app estará em <nome>.streamlit.app.

Cada git push faz rebuild automático.

6. Personalização
Cores: hsv_palette() em app.py (seção 3.1)

Tema: edite .streamlit/config.toml

Logo: substitua static/logo_trt1_horizontal.png

Tipos de desenho: parámetros de Draw() em app.py

