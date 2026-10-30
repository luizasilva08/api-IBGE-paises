import requests

print ("==== API - Dados de Países ====\n")

paises = """
AF - Afeganistão
ZA - África do Sul
AL - Albânia
DE - Alemanha
AD - Andorra
AO - Angola
AG - Antígua e Barbuda
SA - Arábia Saudita
DZ - Argélia
AR - Argentina
AM - Armênia
AU - Austrália
AT - Áustria
AZ - Azerbaijão
BS - Bahamas
BD - Bangladesh
BB - Barbados
BH - Barein
BY - Belarus
BE - Bélgica
BZ - Belize
BJ - Benin
BO - Bolívia
BA - Bósnia e Herzegovina
BW - Botsuana
BR - Brasil
BN - Brunei
BG - Bulgária
BF - Burkina Faso
BI - Burundi
BT - Butão
CV - Cabo Verde
CM - Camarões
KH - Camboja
CA - Canadá
QA - Catar
KZ - Cazaquistão
TD - Chade
CL - Chile
CN - China
CY - Chipre
CO - Colômbia
KM - Comores
CG - Congo
CI - Costa do Marfim
CR - Costa Rica
HR - Croácia
CU - Cuba
DK - Dinamarca
DJ - Djibouti
DM - Dominica
EG - Egito
SV - El Salvador
AE - Emirados Árabes Unidos
EC - Equador
ER - Eritréia
SK - Eslováquia
SI - Eslovênia
ES - Espanha
US - Estados Unidos da América
EE - Estônia
SZ - Eswatini
ET - Etiópia
FJ - Fiji
PH - Filipinas
FI - Finlândia
FR - França
GA - Gabão
GM - Gâmbia
GH - Gana
GE - Geórgia
GD - Granada
GR - Grécia
GT - Guatemala
GY - Guiana
GN - Guiné
GQ - Guiné Equatorial
GW - Guiné-Bissau
HT - Haiti
NL - Holanda
HN - Honduras
HU - Hungria
YE - Iêmen
MH - Ilhas Marshall
SB - Ilhas Salomão
IN - Índia
ID - Indonésia
IR - Irã
IQ - Iraque
IE - Irlanda
IS - Islândia
IL - Israel
IT - Itália
JM - Jamaica
JP - Japão
JO - Jordânia
KI - Kiribati
KW - Kuwait
LA - Laos
LS - Lesoto
LV - Letônia
LB - Líbano
LR - Libéria
LY - Líbia
LI - Liechtenstein
LT - Lituânia
LU - Luxemburgo
MK - Macedônia do Norte
MG - Madagáscar
MY - Malásia
MW - Malauí
MV - Maldivas
ML - Mali
MT - Malta
MA - Marrocos
MU - Maurício
MR - Mauritânia
MX - México
MM - Mianmar
FM - Micronésia
MZ - Moçambique
MD - Moldávia
MC - Mônaco
MN - Mongólia
ME - Montenegro
NA - Namíbia
NR - Nauru
NP - Nepal
NI - Nicarágua
NE - Níger
NG - Nigéria
NO - Noruega
NZ - Nova Zelândia
OM - Omã
PW - Palau
PA - Panamá
PG - Papua Nova Guiné
PK - Paquistão
PY - Paraguai
PE - Peru
PL - Polônia
PT - Portugal
KE - Quênia
KG - Quirguistão
GB - Reino Unido
CF - República Centro Africana
KR - República da Coréia
CD - República Democrática do Congo
DO - República Dominicana
KP - República Popular Democrática da Coréia
CZ - República Tcheca
RO - Romênia
RW - Ruanda
RU - Rússia (Federação Russa)
WS - Samoa
SM - San Marino
LC - Santa Lúcia
KN - São Cristóvão e Nevis
ST - São Tomé e Príncipe
VC - São Vicente e Granadinas
SC - Seichelles
SN - Senegal
SL - Serra Leoa
RS - Sérvia
SG - Singapura
SY - Síria
SO - Somália
LK - Sri Lanka
SD - Sudão
SS - Sudão do Sul
SE - Suécia
CH - Suíça
SR - Suriname
TJ - Tadjiquistão
TH - Tailândia
TZ - Tanzânia
TL - Timor Leste
TG - Togo
TO - Tonga
TT - Trinidad e Tobago
TN - Tunísia
TM - Turcomenistão
TR - Turquia
TV - Tuvalu
UA - Ucrânia
UG - Uganda
UY - Uruguai
UZ - Uzbequistão
VU - Vanuatu
VE - Venezuela
VN - Vietnã
ZM - Zâmbia
ZW - Zimbábue
"""
print(f"Países para consultar: {paises}\n")

pais = str(input("\033[034mEscolha um país para consultar (ex: BR, US):\033[m "))

url = f"https://servicodados.ibge.gov.br/api/v1/paises/{pais}"

parametros = {
    "lang": "PT" #pode trocar para EU (inglês) ou ES (espanhol)
}

resposta = requests.get(url)

if resposta.status_code == 200:

    print("\n\033[036mRequisição realizada com sucesso!\033[m\n")
    dados = resposta.json()

    area = dados[0]["area"]["total"]  #o [0] é o indice, precisa ser um número
    print(f"\033[031mÁrea total: {area} km²\033[m\n")

    linguas = dados[0]["linguas"][0]["nome"]
    print(f"\n\033[036mLíngua: {linguas}\033[m\n")

    continente = dados[0]["localizacao"]["regiao"]["nome"]
    sub_continente = dados[0]["localizacao"]["sub-regiao"]["nome"]
    print(f"\n\033[032mContinente: {continente}\033[m\n")
    print(f"\n\033[035mSub-região: {sub_continente}\033[m\n")

    capital = dados[0]["governo"]["capital"]["nome"]
    print(f"\n\033[033mCapital do país: {capital}\033[m\n")

    moeda = dados[0]["unidades-monetarias"][0]["nome"]
    print(f"\n\033[034mMoeda: {moeda}\033[m\n")

    historico = dados[0]["historico"]
    print(f"\n\033[036mHistória do país:\033[m\n {historico}")


else:
    print("\n\033[031mErro na requisição.\033[m")