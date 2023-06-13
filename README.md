# search-cpp-module

- Script to explore projects that use C++ modules from the [awesome-cpp](https://github.com/fffaraz/awesome-cpp)

Investigation involves examining popular C++ projects listed in the README of the [Awesome Cpp](https://github.com/fffaraz/awesome-cpp) repository, which provides links to various open-source C++ projects. The README of Awesome Cpp contains XXX links to C++ open-source projects. These projects were then individually searched using the GitHub Search API. The objective was to determine whether these well-known projects were utilizing C++ modules.

Each API call contains a query of this form.

![sample](./querySample.png)

- It searches whether the project has specific file extensions like `cppm`, `ixx`, `ccm`, `cxxm` and `cxx`.
- It changes the `org` value for different projects.

## Searching Criteria

This script have verified whether repositories contain files for modules or not. Each compiler utilizes specific file extensions for C++ modules. For instance, MSVC employs the `ixx` extension for files that define the interface of modules. 

```python
self.msvc_extension = ["ixx"]
self.clang_extension = ["cppm", "ccm", "cxxm"]
self.gcc_extension = ["cxx"]
```

Therefore, if a repository includes modules, we can conclude that it contains a file with a module extension that defines the interface of the module.

## Result

The results show that all projects listed in [Awesome Cpp](https://github.com/fffaraz/awesome-cpp) do not use C++ modules. We can say that the compiler's lack of full support for C++ module features has had a significant impact on the utilization of module features.