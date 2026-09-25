import assert from "node:assert/strict";
import { test } from "node:test";
import hre from "hardhat";

test("should register and retrieve content", async () => {
  const { viem } = await hre.network.connect();

  const provenance = await viem.deployContract("Provenance");

  await provenance.write.registerContent([
    "VT-001",
    "sha256-original-123",
    "phash-original-456",
    "user123",
    "",
    "original"
  ]);

  const content = await provenance.read.getContent(["VT-001"]);

  assert.equal(content.contentId, "VT-001");
  assert.equal(content.sha256Hash, "sha256-original-123");
  assert.equal(content.perceptualHash, "phash-original-456");
  assert.equal(content.creatorId, "user123");
  assert.equal(content.parentId, "");
  assert.equal(content.editType, "original");
});


test("should verify the correct SHA-256 hash", async () => {
  const { viem } = await hre.network.connect();

  const provenance = await viem.deployContract("Provenance");

  await provenance.write.registerContent([
    "VT-002",
    "sha256-test-123",
    "phash-test-456",
    "user456",
    "",
    "original"
  ]);

  const result = await provenance.read.verifyContent([
    "VT-002",
    "sha256-test-123"
  ]);

  assert.equal(result, true);
});


test("should reject an incorrect SHA-256 hash", async () => {
  const { viem } = await hre.network.connect();

  const provenance = await viem.deployContract("Provenance");

  await provenance.write.registerContent([
    "VT-003",
    "sha256-correct",
    "phash-test",
    "user789",
    "",
    "original"
  ]);

  const result = await provenance.read.verifyContent([
    "VT-003",
    "sha256-wrong"
  ]);

  assert.equal(result, false);
});

test("should add an edit linked to its parent", async () => {
  const { viem } = await hre.network.connect();

  const provenance = await viem.deployContract("Provenance");

  // Register original content
  await provenance.write.registerContent([
    "IMG-001",
    "sha256-original",
    "phash-original",
    "user123",
    "",
    "original"
  ]);

  // Add edited content
  await provenance.write.addEdit([
    "IMG-002",
    "sha256-edited",
    "phash-edited",
    "user123",
    "IMG-001",
    "crop"
  ]);

  // Read the edited content
  const edited = await provenance.read.getContent(["IMG-002"]);

  assert.equal(edited.contentId, "IMG-002");
  assert.equal(edited.sha256Hash, "sha256-edited");
  assert.equal(edited.parentId, "IMG-001");
  assert.equal(edited.editType, "crop");
});
