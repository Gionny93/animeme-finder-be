from application import app, fetch_data

if __name__ == "__main__":
    import sys
    import unittest

    if len(sys.argv) == 2 and sys.argv[1] == "test":
        test_suite = unittest.TestLoader().discover("tests")
        unittest.TextTestRunner().run(test_suite)
    else:
        app.run()

