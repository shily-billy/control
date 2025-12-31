from typer import Typer

from app.common.log import console

app = Typer(help="Control SuperPanel CLI")


@app.command()
def status():
    """نمایش وضعیت اسکلت پروژه."""
    console.print("control: ok")


@app.command()
def sync(target: str = "all"):
    """همگام‌سازی داده‌ها از پنل‌ها (اسکلت)."""
    console.print(f"sync started: {target}")


@app.command()
def report(range: str = "today"):
    """گزارش‌گیری (اسکلت)."""
    console.print(f"report: {range}")


if __name__ == "__main__":
    app()
