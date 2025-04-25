class APIHub:
    """
    A central hub for managing and routing API calls.

    This class manages a collection of APIs and routes incoming API calls
    to the appropriate API based on a defined naming convention.
    """

    def __init__(self):
        """
        Initializes the APIHub with an empty API dictionary.
        """
        self.apis = {}

    def initialize_apis(self, api_list):
        """
        Initializes the API hub with a list of APIs.

        Args:
            api_list (list): A list of APIs, each following the convention
                             'ClassName_method_Name=APIClass'.
        Raises:
            ValueError: If the API format is incorrect.
        """
        for api_def in api_list:
            try:
                api_name, api_class = api_def.split("=")
                class_name, method_name = api_name.split("_", 1)
                if class_name not in self.apis:
                    self.apis[class_name] = {}
                self.apis[class_name][method_name] = eval(api_class)

            except ValueError:
                raise ValueError(
                    "Incorrect API format. Expected format: 'ClassName_method_Name=APIClass'"
                )
            except NameError:
                raise NameError(f"API Class '{api_class}' is not defined.")

    def route_api_call(self, api_call, *args, **kwargs):
        """
        Routes an API call to the appropriate API method.

        Args:
            api_call (str): The API call string in the format 'ClassName_method_Name'.
            *args: Variable length argument list for the API method.
            **kwargs: Arbitrary keyword arguments for the API method.

        Returns:
            The result of the API call.

        Raises:
            ValueError: If the API call format is incorrect.
            KeyError: If the API class or method is not found.
            TypeError: If the API call can't be performed.
        """
        try:
            class_name, method_name = api_call.split("_", 1)
            api_class = self.apis[class_name][method_name]
            api_instance = api_class()
            method = getattr(api_instance, method_name)
            result = method(*args, **kwargs)
            return result
        except ValueError:
            raise ValueError(
                "Incorrect API call format. Expected format: 'ClassName_method_Name'"
            )
        except KeyError:
            raise KeyError(f"API call '{api_call}' not found.")
        except TypeError:
            raise TypeError(f"API call '{api_call}' cannot be performed.")