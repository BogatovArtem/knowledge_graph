from py2neo import Graph, Path, Node, Relationship

graph = Graph("bolt://localhost:11001", auth=("neo4j", "123"))

def create_nodes_article(name_article, doi, authors, data, subjects):
    tx = graph.begin()
    node_article = Node("article", name=name_article, doi=doi, authors=authors, data=data, subjects=subjects)
    tx.create(node_article)
    tx.commit()

    return node_article

def create_nodes_author(name_author):
    tx = graph.begin()
    node_author = Node("author", name=name_author)
    tx.create(node_author)
    tx.commit()

    return node_author

def create_relationship(node_left, name_relationship, node_right):
    tx = graph.begin()
    rel = Relationship(node_left, name_relationship, node_right)
    tx.create(rel)
    tx.commit()

def create_node_ref_art(name, link):
    tx = graph.begin()
    node_ref_article = Node("reference_article", name=name, link=link)
    tx.create(node_ref_article)
    tx.commit()

    return node_ref_article

graph.delete_all()






