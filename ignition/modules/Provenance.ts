import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const ProvenanceModule = buildModule("ProvenanceModule", (m) => {
  const provenance = m.contract("Provenance");

  return { provenance };
});

export default ProvenanceModule;
