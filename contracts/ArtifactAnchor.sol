// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ArtifactAnchor
/// @notice Records off-chain SHA-256 artifact commitments per transaction sender.
/// @dev Does not validate artifact contents, authorship, physical claims, or identity.
///      No token, admin, upgrade, or custody functionality. Deployment is chain-specific.
contract ArtifactAnchor {
    error ZeroDigest();
    error AlreadyAnchored();

    struct Anchor {
        uint256 timestamp;
        bool exists;
    }

    mapping(address => mapping(bytes32 => Anchor)) public anchors;

    event ArtifactAnchored(address indexed publisher, bytes32 indexed digest, uint256 timestamp);

    function anchor(bytes32 digest) external {
        if (digest == bytes32(0)) revert ZeroDigest();
        if (anchors[msg.sender][digest].exists) revert AlreadyAnchored();
        uint256 timestamp = block.timestamp;
        anchors[msg.sender][digest] = Anchor({timestamp: timestamp, exists: true});
        emit ArtifactAnchored(msg.sender, digest, timestamp);
    }
}
