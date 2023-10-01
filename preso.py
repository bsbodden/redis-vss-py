import pandas as pd
import numpy as np
from IPython.display import display, HTML
from matplotlib import pyplot as plt

def create_query_table(client, index, query, queries, encoded_queries, extra_params = {}):
    results_list = []
    for i, encoded_query in enumerate(encoded_queries):
        result_docs = client.ft(index).search(query, { 'query_vector': np.array(encoded_query, dtype=np.float32).tobytes() } | extra_params).docs
        for doc in result_docs:
            vector_score = round(1 - float(doc.vector_score), 2)
            results_list.append({
                'query': queries[i],
                'score': vector_score,
                'id': doc.id,
                'type': doc.type,
                'color': doc.color,
                'description': doc.description
            })

    # Pretty-print the table
    queries_table = pd.DataFrame(results_list)
    queries_table.sort_values(by=['query', 'score'], ascending=[True, False], inplace=True)
    queries_table['query'] = queries_table.groupby('query')['query'].transform(lambda x: [x.iloc[0]] + ['']*(len(x)-1))
    queries_table['description'] = queries_table['description'].apply(lambda x: (x[:497] + '...') if len(x) > 500 else x)
    html = queries_table.to_html(index=False, classes='striped_table')
    display(HTML(html))


def plot_images(rows = 2, columns = 3, images = []):
    fig, axs = plt.subplots(2, 3, figsize=(4, 3))
    [ax.imshow(img) for ax, img in zip(axs.ravel(), images)]
    [ax.axis('off') for ax in axs.ravel()]
    plt.tight_layout()
    plt.show()