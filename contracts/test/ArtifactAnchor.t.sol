// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ArtifactAnchor} from "../ArtifactAnchor.sol";

contract OtherPublisher {
    function publish(ArtifactAnchor registry, bytes32 digest) external {
        registry.anchor(digest);
    }
}

contract ArtifactAnchorTest {
    function testAnchorAndRead() public {
        ArtifactAnchor registry = new ArtifactAnchor();
        bytes32 digest = sha256("research artifact");
        registry.anchor(digest);
        (, bool exists) = registry.anchors(address(this), digest);
        (, bool otherExists) = registry.anchors(address(0xBEEF), digest);
        require(exists, "missing anchor");
        require(!otherExists, "wrong publisher");
    }

    function testDuplicateReverts() public {
        ArtifactAnchor registry = new ArtifactAnchor();
        bytes32 digest = sha256("research artifact");
        registry.anchor(digest);
        (bool success,) = address(registry).call(
            abi.encodeCall(ArtifactAnchor.anchor, (digest))
        );
        require(!success, "duplicate accepted");
    }

    function testZeroDigestReverts() public {
        ArtifactAnchor registry = new ArtifactAnchor();
        (bool success,) = address(registry).call(
            abi.encodeCall(ArtifactAnchor.anchor, (bytes32(0)))
        );
        require(!success, "zero digest accepted");
    }

    function testIndependentPublishers() public {
        ArtifactAnchor registry = new ArtifactAnchor();
        OtherPublisher other = new OtherPublisher();
        bytes32 digest = sha256("same artifact");
        registry.anchor(digest);
        other.publish(registry, digest);
        (, bool firstExists) = registry.anchors(address(this), digest);
        (, bool secondExists) = registry.anchors(address(other), digest);
        require(firstExists, "first missing");
        require(secondExists, "second missing");
    }
}
