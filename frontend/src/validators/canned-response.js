import vest, { test, enforce } from "vest";

const suite = vest.create("CannedResponse", (form = {}, currentField) => {
  console.log(form);

  // If the field name is provided, only validate that field
  vest.only(currentField);

  test("key", "The key must be alphanumeric and less than 32 characters", () =>
    enforce(form.key)
      .matches(/[a-zA-Z0-9]{1,32}/)
      .isNotEmpty()
      .shorterThanOrEquals(32),
  );

  test("title", "The title must be less than 256 characters", () =>
    enforce(form.title).isNotEmpty().shorterThanOrEquals(256),
  );

  test("content", "The response must have some content", () => enforce(form.content).isNotEmpty());

  test(
    "fields",
    "Fields must have a name less than 256 characters and a value less than 1024 characters",
    () =>
      enforce(form.fields).isArrayOf(
        enforce.shape({
          name: enforce.isString().isNotEmpty().lessThanOrEquals(256),
          value: enforce.isString().isNotEmpty().lessThanOrEquals(1024),
        }),
      ),
  );
});

export default suite;
