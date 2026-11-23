# EduRuckus scenario instructions

Maintain the scenario YAML files, `scenarios.schema.yml`, `validate.py`, and
`config.j2` as a consistent configuration system for provisioning RUCKUS FastIron
switches. Use `scenarios/999-test.yml` as the example data set.

## Template requirements

- Generate one switch configuration per render. Pass the selected switch's
  properties as top-level variables and the scenario's shared VLAN list as
  `vlans`: `template.render(vlans=scenario.get("vlans", []), **switch)`.
- Treat `scenarios.schema.yml` as the source of truth for variables, required
  properties, and defaults. Apply schema defaults in the template when variables
  are omitted; JSON Schema validation does not populate them.
- Emit optional settings without schema defaults only when their values are
  defined. Preserve explicit `false` values, including OSPF passive settings and
  BGP neighbor activation, and handle omitted optional collections safely.
- Cover VLANs, physical interfaces, loopbacks, VEs, switched and routed LAGs,
  IPv4 and IPv6 addressing, speeds, MTUs, ACLs, OSPF, BGP, and free-text settings.
- Preserve local and remote ASN representations from YAML. An asdot value such
  as `"1.5400"` must remain `1.5400`; do not convert between asdot and asplain.
- Interpret free-text `config` values as complete CLI commands in their enclosing
  scope. Switch configuration uses global scope; port and LAG configuration uses
  the corresponding interface scope; interface OSPF configuration uses interface
  scope; neighbor configuration uses BGP scope. Preserve command order and
  relative indentation in multiline values.

## FastIron commands

- When adding or changing CLI commands, verify their exact syntax and scopes in
  official documentation for the latest released FastIron version. Record the
  version and source links in template comments. Start with the
  [RUCKUS documentation catalog](https://support.ruckuswireless.com/documents)
  and the release's command reference and configuration guides.
- Normalize schema interface aliases into FastIron interface names. Ethernet
  ports and LAGs use their configured mode; loopbacks and VEs are routed
  interfaces regardless of the schema's default port mode.
- Create VLANs, LAGs, ACLs, and OSPF areas before referring to them. Include VLANs
  referenced by interfaces even when no name is supplied in the shared VLAN
  list. Preserve ACL entry order.
- Configure VLAN names in the `vlan ... name ... by port` command and tagged or
  untagged membership in VLAN scope. Configure LAG interface settings under
  `interface lag`. A VE's ID must match its VLAN ID.
- Apply IP MTUs to addressed, routed Ethernet, LAG, and VE interfaces. Use the
  switch's `jumbo` setting for Layer 2 frame size. Respect hardware limits and
  supported command scopes, including loopback IDs 1 through 32.
- Use one global `ip router-id` for OSPF and BGP; supplied values must agree.
  Use metric 1 for stub and NSSA areas because the schema provides no metric
  field. Put IPv6 BGP network statements in `address-family ipv6 unicast`.
- Keep IPv6 interface address handling consistent between ports and LAGs,
  including the required CIDR prefix length in the schema and rendered commands.

## Management configuration

Derive the hostname from the switch number using the schema's hostname prefix.
Always configure management interface 1 with address `198.51.100.2{{ number }}`
and mask `255.255.255.192`: switch 1 receives `198.51.100.21/26`, switch 2 receives
`198.51.100.22/26`, and so on.

Create both `admin` and `provision` with password `ruckus` and FastIron privilege
0 for full administrative access:

```text
username admin privilege 0 password ruckus
username provision privilege 0 password ruckus
```

## Jinja formatting and verification

- Render with `lstrip_blocks=True`, `trim_blocks=True`, and `StrictUndefined`.
  Retain the template's `#jinja2` settings directive. When rendering directly
  with Python, consume that directive separately so it is absent from CLI output.
- Use standard Jinja2 features and filters. Indent nested control blocks for
  readability and use literal spaces for CLI indentation. Limit local whitespace
  controls to places where macros require them to preserve their output.
- Run `python3 validate.py` when changing schemas or scenarios. Report validation
  failures with the affected field and cause.
- Check template changes with both example switches and relevant omitted-variable,
  default, explicit-false, multiline, and ASN-format cases. For formatting-only
  edits, compare rendered output byte for byte with the previous template using
  the configured whitespace settings.
- When asked to render the example, write `switch1.conf` and `switch2.conf` in the
  repository root. Refresh requested configurations after template behavior
  changes. Generated `*.conf` files are ignored by Git.
- Preserve unrelated workspace edits and follow `README.md` for scenario naming
  and contribution conventions.
