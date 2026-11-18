# EduRuckus scenarios

The scenarios in this repo are deployed to the EduRuckus switches by the provisioning automation.

## Adding a new scenario

1. Create a new file in the `scenarios/` directory. The filename should be `{sequence number}-{name}.yml`.
    - For the sequence number, pick the next available.
    - The name should be short and follow the snake case naming convention.
    - Example: `14-ospf_stub_area.yml`
1. Add the configuration for at least 2 switches in the new file.
1. Validate the scenarios by running `validate.py`.
1. Commit. Use a meaningful commit message, and described the details in the message's body.
1. Push and create a pull request.
