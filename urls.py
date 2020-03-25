from controllers import *


# FastAPIのルーティング用関数
"""
aad_api_route(path: str, endpoint: Callable, *, response_model: Type[Any] = None,
              status_code: int = 200, tags: List[str] = None,
              dependencies: Sequence[fastapi.params.Depends] = None,
              summary: str = None, description: str = None,
              response_description: str = 'Successful Response',
              responses: Dict[Union[int, str], Dict[str, Any]] = None,
              deprecated: bool = None, methods: List[str] = None,
              operation_id: str = None, response_model_include: Union[Set[Union[int, str]],
              Dict[Union[int, str], Any]] = None, response_model_exclude: Union[Set[Union[int, str]],
              Dict[Union[int, str], Any]] = set(), response_model_by_alias: bool = True,
              response_model_skip_defaults: bool = None, response_model_exclude_unset: bool = False,
              include_in_schema: bool = True,
              response_class: Type[starlette.responses.Response] = None, name: str = None)
"""
app.add_api_route('/', index)
app.add_api_route('/admin', admin, methods=['GET', 'POST'])
app.add_api_route('/register', register, methods=['GET', 'POST']) 
app.add_api_route('/todo/{username}/{year}/{month}/{day}', detail)
app.add_api_route('/done', done, methods=['POST'])
app.add_api_route('/add', add, methods=['POST'])
app.add_api_route('/delete/{t_id}', delete)
app.add_api_route('/logout', logout)

# JSONで返すAPI
app.add_api_route('/get', get)
app.add_api_route('/add_task', insert, methods=['POST'])