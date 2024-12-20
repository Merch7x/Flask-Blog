from flask import current_app


def add_to_index(index, model):
    """Adds model objects to search index"""
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)


def remove_from_index(index, model):
    """Removes models objects from the search index"""
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    """Query an index from the search index"""
    if not current_app.elasticsearch:
        return [], 0
    try:
        search = current_app.elasticsearch.search(
            index=index,
            body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                  'from_': (page - 1) * per_page, 'size': per_page})
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        # total = search['hits']['total']['value']
        return ids, search['hits']['total']['value']
    except Exception as e:
        current_app.logger.error(f"Elasticsearch query failed: {e}")
        return [], 0
