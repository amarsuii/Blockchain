// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title CertificateVerification
 * @dev Smart contract for registering and verifying tamper-resistant certificate SHA-256 hashes.
 */
contract CertificateVerification {
    address public owner;

    struct CertificateRecord {
        string certificateId;
        string certificateHash;
        string issuer;
        uint256 timestamp;
        address registeredBy;
        bool exists;
    }

    // Mapping from unique Certificate ID to certificate record
    mapping(string => CertificateRecord) private certificates;

    // Events
    event CertificateRegistered(
        string indexed certificateId,
        string certificateHash,
        string issuer,
        uint256 timestamp,
        address indexed registeredBy
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Registers a new certificate on the blockchain
     * @param _certificateId Unique identifier for the certificate
     * @param _certificateHash SHA-256 hash of the canonical certificate data
     * @param _issuer Issuer organization name (e.g. Infosys Springboard)
     * @param _timestamp Epoch timestamp of completion/registration
     */
    function registerCertificate(
        string memory _certificateId,
        string memory _certificateHash,
        string memory _issuer,
        uint256 _timestamp
    ) public returns (bool) {
        require(bytes(_certificateId).length > 0, "Certificate ID cannot be empty");
        require(bytes(_certificateHash).length > 0, "Certificate Hash cannot be empty");
        require(!certificates[_certificateId].exists, "Certificate ID already registered");

        certificates[_certificateId] = CertificateRecord({
            certificateId: _certificateId,
            certificateHash: _certificateHash,
            issuer: _issuer,
            timestamp: _timestamp,
            registeredBy: msg.sender,
            exists: true
        });

        emit CertificateRegistered(
            _certificateId,
            _certificateHash,
            _issuer,
            _timestamp,
            msg.sender
        );

        return true;
    }

    /**
     * @notice Verifies if a given certificate hash matches the stored blockchain hash
     * @param _certificateId Certificate ID to verify
     * @param _certificateHash Recalculated SHA-256 hash
     * @return bool True if certificate exists and hash matches exactly, False otherwise
     */
    function verifyCertificate(
        string memory _certificateId,
        string memory _certificateHash
    ) public view returns (bool) {
        if (!certificates[_certificateId].exists) {
            return false;
        }

        return keccak256(abi.encodePacked(certificates[_certificateId].certificateHash)) == 
               keccak256(abi.encodePacked(_certificateHash));
    }

    /**
     * @notice Retrieves stored certificate details from blockchain
     * @param _certificateId Certificate ID
     * @return certificateHash Stored SHA-256 hash
     * @return issuer Organization name
     * @return timestamp Registration timestamp
     * @return registeredBy Address of account that registered the certificate
     */
    function getCertificate(string memory _certificateId)
        public
        view
        returns (
            string memory certificateHash,
            string memory issuer,
            uint256 timestamp,
            address registeredBy
        )
    {
        require(certificates[_certificateId].exists, "Certificate not found on blockchain");

        CertificateRecord memory cert = certificates[_certificateId];
        return (
            cert.certificateHash,
            cert.issuer,
            cert.timestamp,
            cert.registeredBy
        );
    }
}
