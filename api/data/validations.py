import logging
from typing import Any, Callable, Dict

from starlette.exceptions import HTTPException
from starlette.requests import Request


logger: logging.Logger = logging.getLogger("root")


def validate_data(attribute_model: Callable[..., None] | Any):
    def func_wrap(f):
        async def fn(*args, **kwargs):
            try:
                request: Request = args[0]
                params: Dict[str, Any] = getattr(
                        request.state.data_model, "attributes")

                # validate params value with the attribute model
                # at endpoint level
                attribute_model(**params)

            except Exception as err:
                if isinstance(err, TypeError):
                    err_args: str  = getattr(err, "args")[0]
                    detail: str = err_args.split(sep=") ")[-1]

                    logger.exception(err)
                    raise HTTPException(
                        status_code=400, detail=f"Bad request, {detail}")

                logger.exception(err)
                raise HTTPException(status_code=400, detail="Bad request")

            # pass params value of the data_model validated from DataValidationMiddleware
            # as the first layer of validation at middleware level
            return await f(params=params, *args, **kwargs)

        return fn
    return func_wrap
