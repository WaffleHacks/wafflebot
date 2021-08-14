import vest, { test, enforce } from "vest";

const suite = vest.create("Announcement", (form = {}, currentField) => {
  // Only validate field provided
  vest.only(currentField);

  test("name", "The name must be less than 128 characters", () =>
    enforce(form.name).isNotEmpty().shorterThanOrEquals(128),
  );

  test("content", "The announcement must have some content", () =>
    enforce(form.content).isNotEmpty(),
  );

  if (form.embed) {
    test("title", "A title less than 256 characters is required when using an embed", () =>
      enforce(form.content).isNotEmpty().shorterThanOrEquals(256),
    );
  }
});

export default suite;
