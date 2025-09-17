import streamlit as st
import pandas as pd
from collections import Counter
from itertools import chain

# -------------------------
# Funções auxiliares
# -------------------------
def aplicar_regra_homogeneos(elementos, largura):
    matriz = []
    contagem = Counter(elementos)

    for num in list(contagem):
        while contagem[num] >= largura:
            matriz.append([num] * largura)
            contagem[num] -= largura

    restantes = list(chain.from_iterable([[k] * v for k, v in contagem.items()]))
    return matriz, restantes


def aplicar_regra_sequencias(elementos, largura):
    matriz = []
    counter_restantes = Counter(elementos)

    while True:
        if len(counter_restantes) < largura:
            break

        elementos_ordenados = sorted(counter_restantes.items(), key=lambda x: (-x[1], x[0]))
        encontrou = False
        for num, _ in elementos_ordenados:
            sequencia = [num + i for i in range(largura)]
            if all(counter_restantes.get(val, 0) >= 1 for val in sequencia):
                matriz.append(sequencia)
                for val in sequencia:
                    counter_restantes[val] -= 1
                    if counter_restantes[val] == 0:
                        del counter_restantes[val]
                encontrou = True
                break
        if not encontrou:
            break

    restantes = list(chain.from_iterable([[k] * v for k, v in counter_restantes.items()]))
    return matriz, restantes


def gerar_matriz_adaptativa(elementos, largura):
    # --- Teste 1: começar com homogêneos
    blocos1, rest1 = aplicar_regra_homogeneos(elementos, largura)
    blocos1_seq, rest1 = aplicar_regra_sequencias(rest1, largura)
    total1 = len(set(tuple(b) for b in blocos1 + blocos1_seq))

    # --- Teste 2: começar com sequências
    blocos2, rest2 = aplicar_regra_sequencias(elementos, largura)
    blocos2_hom, rest2 = aplicar_regra_homogeneos(rest2, largura)
    total2 = len(set(tuple(b) for b in blocos2 + blocos2_hom))

    # --- Escolher melhor
    if total1 <= total2:
        blocos = blocos1 + blocos1_seq
        restantes = rest1
    else:
        blocos = blocos2 + blocos2_hom
        restantes = rest2

    # --- Regra 3: blocos quaisquer
    for i in range(0, len(restantes), largura):
        blocos.append(restantes[i:i + largura])

    # --- Completar último bloco com o mais frequente
    if blocos and len(blocos[-1]) < largura:
        mais_freq = Counter(elementos).most_common(1)[0][0]
        blocos[-1].extend([mais_freq] * (largura - len(blocos[-1])))

    return blocos


# -------------------------
# Interface Streamlit
# -------------------------
st.title("Gerador de Vetor de Intervalos e Agrupamentos")

st.write("Preencha a tabela abaixo com os intervalos e número de repetições:")

# DataFrame inicial
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {"Início": [1], "Fim": [5], "Repetições": [2]}
    )

# Editor de tabela interativa
df_editado = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    width="stretch"
)

# Input do segundo argumento
largura = st.number_input(
    "Informe a largura",
    min_value=5,
    max_value=10,
    value=5
)

# Botão para gerar vetor e matriz
if st.button("Gerar Vetor e Executar Algoritmo"):

    # 👉 Só aqui atualizamos o session_state com a versão editada
    st.session_state.df = df_editado.copy()

    vetor = []
    # ✅ Aqui usamos o df_editado atualizado
    for _, row in df_editado.iterrows():
        inicio, fim, repeticoes = int(row["Início"]), int(row["Fim"]), int(row["Repetições"])
        for _ in range(repeticoes):
            vetor.append((inicio, fim))

    # Expandindo os intervalos [(x,y)] em valores individuais
    vetor_expandido = []
    for item in vetor:
        if isinstance(item, tuple) and len(item) == 2:
            vetor_expandido.extend(range(item[0], item[1] + 1))
        else:
            vetor_expandido.append(item)

     # Rodar algoritmo
    matriz_final = gerar_matriz_adaptativa(vetor_expandido, largura)

    # Contagem consolidada
    contagem_blocos = Counter(tuple(bloco) for bloco in matriz_final)
    resultado_df = pd.DataFrame(
        [{"Bloco": list(bloco), "Repetições": qtd} for bloco, qtd in contagem_blocos.items()]
    )

    # Ordenar de forma decrescente pelas repetições
    resultado_df = resultado_df.sort_values(by="Repetições", ascending=False).reset_index(drop=True)

    st.subheader("Resultado do Agrupamento (Consolidado e Ordenado)")
    st.dataframe(resultado_df, width='stretch')