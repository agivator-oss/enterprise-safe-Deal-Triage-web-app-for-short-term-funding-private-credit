def test_import_router():
    import backend.api.deals as d

    assert d.router.prefix == "/deals"
