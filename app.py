import streamlit as st
import networkx as nx
import pyvis.network as net
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Análise de Redes U2",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Análise de Redes U2 - Tales Henrique Rocha")

@st.cache_data
def carregar_dados():
    G = nx.les_miserables_graph()
    return G

G = carregar_dados()

def calcular_metricas(graph):
    metricas = {
        "Número de Nós": graph.number_of_nodes(),
        "Número de Arestas": graph.number_of_edges(),
        "Densidade": f"{nx.density(graph):.4f}",
        "Coeficiente de Assortatividade": f"{nx.degree_assortativity_coefficient(graph):.4f}",
        "Coeficiente de Clustering Global": f"{nx.transitivity(graph):.4f}",
        "Componentes Conectados": nx.number_connected_components(graph)
    }
    return metricas

def calcular_centralidades(graph):
    degree_centrality = nx.degree_centrality(graph)
    eigenvector_centrality = nx.eigenvector_centrality(graph, max_iter=1000)
    closeness_centrality = nx.closeness_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(graph)

    df_centralidades = pd.DataFrame({
        'Personagem': list(degree_centrality.keys()),
        'Grau (Degree)': list(degree_centrality.values()),
        'Autovetor (Eigenvector)': list(eigenvector_centrality.values()),
        'Proximidade (Closeness)': list(closeness_centrality.values()),
        'Intermediação (Betweenness)': list(betweenness_centrality.values())
    })
    return df_centralidades

def plotar_distribuicao_grau(graph):
    """Gera e exibe um histograma da distribuição de grau."""
    graus = [grau for no, grau in graph.degree()]
    fig, ax = plt.subplots()
    ax.hist(graus, bins='auto', color='skyblue', rwidth=0.85)
    ax.set_title('Distribuição de Grau dos Nós')
    ax.set_xlabel('Grau')
    ax.set_ylabel('Frequência')
    plt.grid(axis='y', alpha=0.75)
    return fig

st.sidebar.header("Opções")
app_mode = st.sidebar.selectbox(
    "Escolha a Análise:",
    ["Visão Geral e Métricas", "Análise de Centralidade", "Visualização Interativa da Rede"]
)

if app_mode == "Visão Geral e Métricas":
    st.header("Métricas Estruturais da Rede")
    st.write("Abaixo estão as principais métricas que descrevem a estrutura geral da rede.")

    metricas = calcular_metricas(G)
    col1, col2, col3 = st.columns(3)
    col1.metric("Nós", metricas["Número de Nós"])
    col2.metric("Arestas", metricas["Número de Arestas"])
    col3.metric("Componentes Conectados", metricas["Componentes Conectados"])
    
    st.subheader("Significado das Métricas:")
    st.markdown("""
    - **Densidade da Rede:** Mede quão conectada a rede é em comparação com o máximo de conexões possíveis (uma rede completa). Um valor próximo de 1 significa uma rede densa, enquanto um valor próximo de 0 indica uma rede esparsa.
      - **Valor:** `{}`
    - **Coeficiente de Assortatividade:** Mede a tendência de nós se conectarem a outros nós de grau semelhante. Um valor positivo indica que nós de alto grau tendem a se conectar com outros de alto grau (assortativo). Um valor negativo indica o oposto (disassortativo).
      - **Valor:** `{}`
    - **Coeficiente de Clustering Global (Transitividade):** Mede a probabilidade de que dois vizinhos de um nó também sejam vizinhos entre si. É uma medida de quão "agrupada" a rede está em triângulos.
      - **Valor:** `{}`
    - **Componentes Conectados:** Indica o número de subgrafos nos quais todos os nós estão conectados entre si. Uma rede totalmente conectada tem apenas 1 componente.
    """.format(metricas['Densidade'], metricas['Coeficiente de Assortatividade'], metricas['Coeficiente de Clustering Global']))

    st.header("Distribuição de Grau")
    st.write("O histograma abaixo mostra a frequência de cada grau (número de conexões) na rede. A maioria dos nós tende a ter poucas conexões, um comportamento típico de redes 'scale-free'.")
    fig_grau = plotar_distribuicao_grau(G)
    st.pyplot(fig_grau)

elif app_mode == "Análise de Centralidade":
    st.header("Análise de Centralidade")
    
    df_centralidades = calcular_centralidades(G)
    
    st.subheader("Ranking de Personagens por Centralidade")
    metrica_selecionada = st.selectbox(
        "Selecione a métrica de centralidade para ordenar:",
        ['Grau (Degree)', 'Autovetor (Eigenvector)', 'Proximidade (Closeness)', 'Intermediação (Betweenness)']
    )

    df_sorted = df_centralidades.sort_values(by=metrica_selecionada, ascending=False).reset_index(drop=True)
    st.dataframe(df_sorted, height=500)

    st.subheader("Significado das Métricas de Centralidade:")
    st.markdown("""
    - **Grau (Degree Centrality):** Mede o número de conexões diretas de um nó. Um nó com alto grau é um "hub" ou conector popular.
    - **Intermediação (Betweenness Centrality):** Mede a frequência com que um nó aparece nos caminhos mais curtos entre outros pares de nós. Nós com alta intermediação são "pontes" que controlam o fluxo de informação na rede.
    - **Proximidade (Closeness Centrality):** Mede a média da distância de um nó a todos os outros nós da rede. Nós com alta proximidade podem espalhar informação de forma eficiente.
    - **Autovetor (Eigenvector Centrality):** Mede a influência de um nó na rede. Uma alta pontuação significa que o nó está conectado a outros nós também muito influentes.
    """)

elif app_mode == "Visualização Interativa da Rede":
    st.header("Visualização Interativa da Rede")

    k = st.sidebar.slider("Destacar os 'k' nós mais importantes:", min_value=1, max_value=15, value=5, step=1)
    centrality_metric = st.sidebar.selectbox(
        "Métrica para destacar os nós:",
        ['Grau (Degree)', 'Intermediação (Betweenness)', 'Autovetor (Eigenvector)'],
        key='viz_metric'
    )
    
    df_centralidades = calcular_centralidades(G)
    top_k_nodes = df_centralidades.nlargest(k, centrality_metric)['Personagem'].tolist()

    net_viz = net.Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True, directed=False)
    
    for node in G.nodes():
        node_size = G.degree(node) * 2 
        if node in top_k_nodes:
            color = "#FF4B4B"
            node_size = 50
        else:
            color = "#00BFFF"
        
        net_viz.add_node(node, title=f"{node} (Grau: {G.degree(node)})", size=node_size, color=color)

    for u, v in G.edges():
        net_viz.add_edge(u, v)

    net_viz.show_buttons(filter_=['physics'])
    
    try:
        path = '/tmp'
        net_viz.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=800)
    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar a visualização: {e}")
        st.write("Isso pode acontecer em alguns ambientes. Tente recarregar a página.")