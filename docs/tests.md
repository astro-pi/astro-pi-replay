# Unit tests


There is also a specific profile for testing the `picamzero` stub, which can be executed using `make test_picamzero`.

# Integration tests

The integration tests run on the `main` branch, and ensure
that the assets schemas are in sync with `main`, and that the
dependencies can be installed.

When needing to run the integration test multiple times (e.g. debugging a failing test), then it's recommended to enable asset caching
by setting the `ASTRO_PI_REPLAY_INTEGRATION_TEST_CACHE` environment variable to `true`. Setting this will store downloaded asset zip files into `.pytest_cache`. The cache can be removed by executing `pytest --cache-clear`.

Additionally, when running locally you will need to configure your environment to have AWS credentials in order to fetch the assets from AWS S3. This can be done, for example, by setting the `AWS_PROFILE`, or using the 1password `op` client.

# Smoke tests

TODO
