from app.tools.telemetry_catalog import (
    get_telemetry_catalog,
    format_telemetry_catalog,
)


def main():
    catalog = get_telemetry_catalog(
        "INC-001"
    )

    print("\n===================================")
    print("TraceRoot Telemetry Catalog")
    print("===================================\n")

    print(
        format_telemetry_catalog(
            catalog
        )
    )


if __name__ == "__main__":
    main()