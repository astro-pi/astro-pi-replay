Now:
-----

- Create CI for PRs to `main` branch that
 - runs tests and build
 - passing tests required to merge
- Create CI for `main` that run same build and test, any system or integration tests,
and then promotes to the `test` env.

- Smoke tests: download package from PyPi and check that functions are callable

Medium-term:
------------
- Add dependabot
- Terraform some infrastructure for S3 (probably in a different repo!)
- Calculate regression of number of students expected
Later:
------
- PR hook - version number checker.
replace "Mission Space Lab" with the new name.
replace astro_pi_executor and Astro Pi Executor with the new name
