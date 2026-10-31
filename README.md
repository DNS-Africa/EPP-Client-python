# Simple Python EPP Client

An epp client transport class. This is just the raw TCP IP protocol. The XML data needs to be handled separately.
The EPP transport protocol is defined at http://tools.ietf.org/html/rfc5734 it looks complicated but is
actually very simple and elegant.

The actual data should be XML data formated according to RFC5730-RFC5733
No validation of any data takes place in this Class

## Usage:

### Getting the image

The image is publicly available
```shell
docker pull dnsbusiness/epp-client:dev
```

### Operating modes
#### Specifying list of template files:
```shell
docker run --rm -v /templates:/templates dnsbusiness/epp-client:dev /templates/first_command.xml
```

#### Pipe XML data from stdin:
```shell
cat templates/domain_info.xml | docker run -i dnsbusiness/epp-client:dev 
```

### Using certificate:
To access certificate files you will need to map the directrory or file into the image using -v.  Multiple -v arguments are possible.
```shell
docker run --rm -i -v /certs:/certs dnsbusiness/epp-client:dev -c /certs/mycert.crt
```

### Other options:

```shell
Options:
  -h, --help            show this help message and exit
  --host=HOST, --ip=HOST
                        Host to connect to [127.0.0.1]
  -p PORT, --port=PORT  Port to connect to [3121]
  -c CERT, --cert=CERT  SSL certificate to use for authenticated connections
  -v, --verbose         Show the EPP server greeting and other debug info
  -u USERNAME, --username=USERNAME
                        Username to login with. If not specified will assume
                        one of the provided files will do the login.
  --password=PASSWORD   Password to login with
  --ng                  Do not wait for an EPP server greeting
  -t, --testing         Do not connect to the server just output the completed
                        templates
  -d DEFS, --define=DEFS
                        For scripting, any fields to be replaced (python
                        dictionary subsitution). Eg: -d DOMAIN=test.co.za will
                        replace %(DOMAIN)s with test.co.za
  --svc=SVC             Add a services sent with the epp login command --svc
                        'urn:ietf:params:xml:ns:host-1.0'
  --svc-ext=SVC_EXT     Add a services extensions sent with the epp login
                        command --svc-ext 'urn:ietf:params:xml:ns:secDNS-1.1'
```

## Building the image

Versioning follows the workspace standard (`../AGENTS.md` § "Versioning &
release"). The source version lives in the `VERSION` file (`X.Y.Z`).

- `make push` — dev/beta image, buildx multi-arch, tagged
  `dnsbusiness/epp-client:<dev|branch>`: `dev` on `main`/`master`, otherwise
  the branch name with `/` and `-` → `_` (e.g. `feature/foo` → `:feature_foo`;
  override with `BRANCH=<name>`). The version
  `<X.Y.Z>-<dev|branch>_<YYYYMMDDHHmm>` is baked into the image via the
  `SOURCE_BRANCH` build-arg. Image only — no commits, no tags, worktree-safe.
- `make publish` — full release: bumps `VERSION` (default patch/build,
  `BUMP=minor|major`, `NEXT=x.y.z`, or `VERSION_BUMP=false`), commits
  `release: version X.Y.Z`, creates the bare tag `X.Y.Z` and pushes branch +
  tag. CI builds the release image `epp-client:X.Y.Z` from the tag. Publish
  only from the main checkout on the default branch, never from a worktree.
- `make` with no target shows usage and builds/pushes nothing.

There is no test suite by design (this is a manual EPP test client), so
publish has no test gate. For a local check: `make build` for an image, or
`python3 epp.py -t templates/domain_info.xml` to render a command without
connecting.

Worktrees: create them as siblings under the workspace root —
`git -C EPP-Client-python worktree add ../.worktrees/epp-client-python/<branch> <branch>` —
and keep them on a real branch; `make push` there tags from that worktree's
own branch. See `../AGENTS.md` § "Git worktrees".
