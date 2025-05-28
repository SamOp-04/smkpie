from unittest.mock import Mock

def mock_supabase():
    mock = Mock()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        'id': 'test', 
        'alert_email': 'test@example.com'
    }]
    return mock