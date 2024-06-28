# GT06

[中文](./README_ZH.md) | English

## Introduction

- GT06 is a universal vehicle GPS positioning communication protocol, implemented based on TCP protocol.
- This project implements the GT06 protocol **client** function based on QuecPython. Users can directly use this function to interact with the corresponding server within the standard.

**Note:**

- The GT06 protocol stipulates fewer messages. The project only implements basic message functions. Customized messages for different service platforms require secondary development, and extended messages also require interface adjustments.
- QuecPython does not implement Unicode name escaping, and the message sent by the GT06 server contains unicode encoded data, so it cannot be transferred. Please note here.

## Functions

- Server connection
- Terminal login
- Terminal GPS & LBS positioning information reporting
- Reporting terminal device status information
- Server command issuance and response

## Usage

- [API Reference Manual](./docs/en/API_Reference.md)
- [Instruction Manual](./docs/en/Instruction_Manual.md)
- [Client Example Code](./code/test_gt06.py)

## Contribution

We welcome contributions to improve this project! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the Apache License. See the [LICENSE](./LICENSE) file for details.

## Support

If you have any questions or need support, please refer to the [QuecPython documentation](https://python.quectel.com/doc/en) or open an issue in this repository.
