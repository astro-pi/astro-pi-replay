from test_utils import raspberry_pi_os_only

def when_run_should_not_fail_and_return_data():
    pass

# integration test
@raspberry_pi_os_only
def test_detect_mode_should_return_Live():
    pass

# integration test
@raspberry_pi_os_only
def test_when_live_mode_should_install_deps_into_venv():
    args = {
        "mode": ExecutionMode.LIVE
    }
    args = Namespace(**args)
    astro_pi_executor.main._main(args)


@raspberry_pi_os_only
def test_executor_live_mode_should_call_underlying_libraries():
    executor = AstroPiExecutor(replay_mode=False)
    # TODO how to test that the underlying libraries are called...
    python_code = "\n".join([
        "from sense_hat import SenseHat",
        "sh = SenseHat()"
        "print(sh.colour.rgb)"
    ])
    executor.run(python_code)
    pass

