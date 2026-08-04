from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
try:
    t = env.get_template("dashboard.html")
    print("Template compiles OK")
except Exception as e:
    print("TEMPLATE ERROR:", repr(e))
