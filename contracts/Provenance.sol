// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Provenance {

    struct Content {
        string contentId;
        string sha256Hash;
        string perceptualHash;
        string creatorId;
        uint256 timestamp;
        string parentId;
        string editType;
    }

    mapping(string => Content) private contents;

    event ContentRegistered(
        string contentId,
        string creatorId,
        string parentId,
        string editType
    );

    function registerContent(
        string memory contentId,
        string memory sha256Hash,
        string memory perceptualHash,
        string memory creatorId,
        string memory parentId,
        string memory editType
    ) public {

        require(
            bytes(contents[contentId].contentId).length == 0,
            "Content already exists"
        );

        contents[contentId] = Content(
            contentId,
            sha256Hash,
            perceptualHash,
            creatorId,
            block.timestamp,
            parentId,
            editType
        );

        emit ContentRegistered(
            contentId,
            creatorId,
            parentId,
            editType
        );
    }

    function addEdit(
    string memory contentId,
    string memory sha256Hash,
    string memory perceptualHash,
    string memory creatorId,
    string memory parentId,
    string memory editType
) public {

    require(
        bytes(contents[parentId].contentId).length != 0,
        "Parent content not found"
    );

    require(
        bytes(contents[contentId].contentId).length == 0,
        "Content already exists"
    );

    contents[contentId] = Content(
        contentId,
        sha256Hash,
        perceptualHash,
        creatorId,
        block.timestamp,
        parentId,
        editType
    );

    emit ContentRegistered(
        contentId,
        creatorId,
        parentId,
        editType
    );
}

    function verifyContent(
        string memory contentId,
        string memory sha256Hash
    ) public view returns (bool) {

        return keccak256(
            bytes(contents[contentId].sha256Hash)
        ) == keccak256(
            bytes(sha256Hash)
        );
    }

    function getContent(
        string memory contentId
    ) public view returns (Content memory) {

        require(
            bytes(contents[contentId].contentId).length != 0,
            "Content not found"
        );

        return contents[contentId];
    }

    function getProvenance(
    string memory contentId
) public view returns (Content[] memory) {

    require(
        bytes(contents[contentId].contentId).length != 0,
        "Content not found"
    );

    // Count how many versions are in the chain
    uint256 count = 1;
    string memory currentId = contentId;

    while (bytes(contents[currentId].parentId).length != 0) {
        currentId = contents[currentId].parentId;
        count++;
    }

    // Create an array large enough for the whole chain
    Content[] memory history = new Content[](count);

    // Fill the array from original -> current
    currentId = contentId;
    uint256 index = count;

    while (bytes(currentId).length != 0) {
        index--;
        history[index] = contents[currentId];
        currentId = contents[currentId].parentId;
    }

    return history;
}
}

