import streamlit as st
import pandas as pd
import re
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json
import requests
import time
from random import randint

st.set_page_config(page_title='Alpha Sender', layout='centered', initial_sidebar_state='collapsed',
                   page_icon=r"alpha logo.png")

# st.markdown()

# #MainMenu{
#     visibility: hidden
# }

st.markdown('''


<style>
.stAlert {
    background-color: #DB650B
}
body {
text-align: center
}

p {
text-align: center
}

.css-5uatcg.edgvbvh5{
    background-color: #DB650B
}
.css-1lsmgbg.egzxvld0{
    visibility: hidden
}

.css-15zrgzn.e16nr0p32{
    visibility: hidden
}

.css-12pn0kf.e16nr0p32{
    visibility: hidden
}

.viewerBadge_container__1QSob {
    visibility: hidden
}
</style>
''', unsafe_allow_html=True)


def add_logo():
    ...
    # st.markdown(
    #     """
    #     <style>
    #         [data-testid="stAppViewContainer"] {
    #             background-image: url(http://placekitten.com/200/200);
    #             background-repeat: no-repeat;
    #             display: block;
    #             margin-left: auto;
    #             margin-right: auto;
    #             width: 8%
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )


def criar_mensagem(message, table, telefones, tokenapi, serviceid, site, tempo):
    pattern = r"{\w+}"
    table = table.fillna('')
    variaveis = re.findall(pattern, message)
    resultado = [i[1:-1] for i in variaveis]
    mensagens = list()
    for tel in table[telefones]:
        for j in resultado:
            for i in table[j]:
                mensagem_ok = message.replace('{' + str(j) + '}', str(i))
                mensagens.append(mensagem_ok)
    # cabeçalho
    headers = {
        'accept': 'application/json',
        'Authorization': tokenapi,
        'Content-Type': 'application/json',
    }
    for mens, cel, porcentagem in zip(mensagens, table[telefones], range(len(table[telefones]))):
        payload = {"serviceId": serviceid, 'number': cel, 'text': mens}
        data = json.dumps(payload)
        response = requests.post(endpoint, headers=headers, data=data)
        time.sleep(randint(tempo[0], tempo[1]))
        resposta = response.json()
        print(resposta)

    return 'OK'


with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        # add_logo()
        st.title('Disparador Digisac')
        st.subheader(f'Olá, {name}')

        # API MENU
        api = st.sidebar.expander('API')
        tokenapi = api.text_input('Token', placeholder='Bearer xxxxxxxxxxxxxxxxxxxxx')
        serviceid = api.text_input('Service ID', placeholder='xxxx-xxxxxx-xxxx')
        endpoint = api.text_input('Endpoint API', placeholder='https://xxxxxxxxx.digisac.chat/api/v1/messages')

        # DISPARO MENU
        tempo = st.sidebar.expander('Disparo')
        segundos = tempo.slider('Tempo entre disparos:', 0, 120, [5, 30])
        tempo.write(f'Entre {segundos[0]} e {segundos[1]} segundos')

        arquivo = st.file_uploader('Suba um mailing aqui: ', 'csv')

        if arquivo:
            a, b = st.columns(2)

            with a:
                with st.container():
                    st.header('Colunas')
                    tabela = pd.read_csv(arquivo, sep=';', encoding='latin1')
                    for i in tabela.columns.values:
                        st.error(i)
            with b:
                st.header('Mensagem')
                mensagem = st.text_area('',
                                        placeholder='Digite a mensagem a ser disparada e coloque as variáveis entre chaves { }')

                gerar_previa = st.button('Prévia')
                st.header('Contatos')
                contatos = st.selectbox('Numeros para enviar', options=tabela.columns.values)

            st.write(f'Total de contatos: {len(tabela[contatos])}')
            if mensagem and contatos and tokenapi and serviceid and endpoint:
                disparar = st.button('Disparar!', type='primary', on_click=criar_mensagem, args=(mensagem, tabela,
                                                                                                 contatos, tokenapi,
                                                                                                 serviceid, endpoint,
                                                                                                 segundos))

        logout = authenticator.logout('Logout', 'sidebar')

    elif authentication_status:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

    # try:
    #     if authenticator.register_user('Register user', preauthorization=False):
    #         st.success('User registered successfully')
    # except Exception as e:
    #     st.error(e)
