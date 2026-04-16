from add import add


def main():
    first = float(input("Enter the first number: "))
    second = float(input("Enter the second number: "))
    result = add(first, second)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
