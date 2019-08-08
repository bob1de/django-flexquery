# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## 2.1.0 - Unreleased
### Added
* Added `django_flexquery.contrib.for_user.ForUserFlexQuery`
### Changed
* Changed directory structure of unittests


## 2.0.0 - 2019-08-06
## Added
* Added `FlexQuery.call_bound()` method as a hook to preprocess custom arguments.
### Changed
* Significantly simplified API:
  It's straightforward to build a Q function that produces a sub-query, hence
  `FlexQuery` types can now only be created from Q functions, simplifying both code
  and unittests a lot.
* Custom functions now get the base QuerySet as first argument.


## 1.0.1 - 2019-07-29
### Added
* Initial release
