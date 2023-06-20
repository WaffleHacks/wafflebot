-- CreateTable
CREATE TABLE "events" (
    "id" INTEGER NOT NULL,
    "discord_id" TEXT NOT NULL,

    CONSTRAINT "events_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "events_discord_id_key" ON "events"("discord_id");
