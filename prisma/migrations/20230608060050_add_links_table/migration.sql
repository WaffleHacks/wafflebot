-- CreateTable
CREATE TABLE "links" (
    "discord_id" TEXT NOT NULL,
    "participant_id" INTEGER NOT NULL,

    CONSTRAINT "links_pkey" PRIMARY KEY ("discord_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "links_participant_id_key" ON "links"("participant_id");
