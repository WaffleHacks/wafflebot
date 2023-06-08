-- AlterEnum
BEGIN;
DELETE FROM settings WHERE key = 'VERIFICATION_CHANNEL';
CREATE TYPE "setting_key_new" AS ENUM ('VERIFICATION_MESSAGE', 'PARTICIPANT_ROLE');
ALTER TABLE "settings" ALTER COLUMN "key" TYPE "setting_key_new" USING ("key"::text::"setting_key_new");
ALTER TYPE "setting_key" RENAME TO "setting_key_old";
ALTER TYPE "setting_key_new" RENAME TO "setting_key";
DROP TYPE "setting_key_old";
COMMIT;
