-- CreateEnum
CREATE TYPE "setting_key" AS ENUM ('VERIFICATION_CHANNEL');

-- CreateTable
CREATE TABLE "settings" (
    "key" "setting_key" NOT NULL,
    "value" TEXT NOT NULL,

    CONSTRAINT "settings_pkey" PRIMARY KEY ("key")
);
