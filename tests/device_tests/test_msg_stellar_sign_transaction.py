# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

# XDR decoding tool available at:
#   https://www.stellar.org/laboratory/#xdr-viewer
#
# ## Test Info
#
# The default mnemonic generates the following Stellar keypair at path 44'/148'/0':
#   GAXSFOOGF4ELO5HT5PTN23T5XE6D5QWL3YBHSVQ2HWOFEJNYYMRJENBV
#   SDK6NSLLKX5UE3DSXGK56MEMTZBOJ6XT3LLA33BEAZUYGO6TXMHNRUPB
#
# ### Testing a new Operation
#
# 1. Start at the Stellar transaction builder: https://www.stellar.org/laboratory/#txbuilder?network=test
#   (Verify that the "test" network is active in the upper right)
#
# 2. Fill out the fields at the top as follows (see DEFAULT_REQUEST):
#   Source account: GAXSFOOGF4ELO5HT5PTN23T5XE6D5QWL3YBHSVQ2HWOFEJNYYMRJENBV
#   Transaction sequence number: 1000
#   Base fee: 100
#   Memo: None
#   Time Bounds: 461535181, 1575234180
#
# 3. Select the operation to test, such as Create Account
#
# 4. Fill out the fields for the operation
#
# 5. Scroll down to the bottom of the page and click "Sign in Transaction Signer"
#
# 6. Copy the generated XDR and add it as a comment to your test case
#
# 7. In the first "Add Signer" text box enter the secret key: SDK6NSLLKX5UE3DSXGK56MEMTZBOJ6XT3LLA33BEAZUYGO6TXMHNRUPB
#
# 8. Scroll down to the signed XDR blob and click "View in XDR Viewer"
#
# 9. Scroll down to the bottom and look at the "signatures" section. The Trezor should generate the same signature
#

from base64 import b64encode
from copy import copy

import pytest

from trezorlib import messages, stellar
from trezorlib.tools import parse_path

pytestmark = [
    pytest.mark.altcoin,
    pytest.mark.stellar,
]

ADDRESS_N = parse_path(stellar.DEFAULT_BIP32_PATH)
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"

EXAMPLE_ACCOUNT = "GBOVKZBEM2YYLOCDCUXJ4IMRKHN4LCJAE7WEAEA2KF562XFAGDBOB64V"
EXAMPLE_ISSUER = "GAUYJFQCYIHFQNS7CI6BFWD2DSSFKDIQZUQ3BLQODDKE4PSW7VVBKENC"
EXAMPLE_SIGNER_KEY = bytes.fromhex(
    "72187adb879c414346d77c71af8cce7b6eaa57b528e999fd91feae6b6418628e"
)

NATIVE_ASSET = messages.StellarAsset(type=messages.StellarAssetType.NATIVE)
ASSET4 = messages.StellarAsset(
    type=messages.StellarAssetType.ALPHANUM4, code="X", issuer=EXAMPLE_ISSUER
)
ASSET12 = messages.StellarAsset(
    type=messages.StellarAssetType.ALPHANUM12,
    code="ABCDEFGHIJKL",
    issuer=EXAMPLE_ISSUER,
)

EXAMPLE_OPERATION = messages.StellarPaymentOp(
    amount=500_111_000,
    destination_account=EXAMPLE_ACCOUNT,
    asset=NATIVE_ASSET,
)

DEFAULT_REQUEST = messages.StellarSignTx(
    source_account="GAXSFOOGF4ELO5HT5PTN23T5XE6D5QWL3YBHSVQ2HWOFEJNYYMRJENBV",
    sequence_number=1000,
    fee=100,
    timebounds_start=461535181,
    timebounds_end=1575234180,
    memo_type=messages.StellarMemoType.NONE,
    num_operations=1,
    network_passphrase=NETWORK_PASSPHRASE,
)


def v(operation, signature, label=None):
    vector_id = operation.__class__.__name__
    if label:
        vector_id += "-" + label
    return pytest.param(operation, signature, id=vector_id)


VECTORS = (
    # operation, signature
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAACwAAAGLG0amyAAAAAAAAAAA=
        messages.StellarBumpSequenceOp(bump_to=424242424242),
        "2xjJi6k8ZU0JwPIA50nWhMr9t8pPYI+WS+D30mHD027wsEGwNtYKMM3AE4oMP5CDr4B5gs2GN34cTxOYSL+cBQ==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAACAAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAA
        messages.StellarAccountMergeOp(destination_account=EXAMPLE_ACCOUNT),
        "cHVT80DSJz1DiAi8ZCXhimyUoMGZMs666lGA4XT2GH4lSL0yod+AgmpSYaeFJtXfiQLEVcMLeS6B6ygMrRNhBg==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAAAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAdzxaYAAAAAAAAAAA=
        messages.StellarCreateAccountOp(
            new_account=EXAMPLE_ACCOUNT, starting_balance=500_111_000
        ),
        "sH6l2uqABZm/I9ZCMAux4oilbbbQmN4f46krh/6EpJ5BxnRBMKIdWTxfx9aOhjMV9veASfYztrjeqEux0r4nBA==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
        messages.StellarPaymentOp(
            amount=500_111_000,
            destination_account=EXAMPLE_ACCOUNT,
            asset=NATIVE_ASSET,
        ),
        "GGmvB49owuJZ+5GA6FCCFoHsj8F+YWojgVEbmFKgqjZobMXcGjyCt8hU1M9nzWFFIVASud/pNKzpzvqwYI2xDQ==",
        label="native_asset",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAFYAAAAAAAAACmElgLCDlg2XxI8Eth6HKRVDRDNIbCuDhjUTj5W/WoVAAAAAB3PFpgAAAAAAAAAAA==
        messages.StellarPaymentOp(
            amount=500_111_000,
            destination_account=EXAMPLE_ACCOUNT,
            asset=ASSET4,
        ),
        "nPrFo5IQ5vESiX9F4fi+zOuZom/TM8ZzO+qPHSxTmC2JnILqtbh91CV8Teao0jVrovjQmmgxLPzOSjgPNYmJBw==",
        label="asset4",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAJBQkNERUZHSElKS0wAAAAAKYSWAsIOWDZfEjwS2HocpFUNEM0hsK4OGNROPlb9ahUAAAAAHc8WmAAAAAAAAAAA
        messages.StellarPaymentOp(
            amount=500_111_000,
            destination_account=EXAMPLE_ACCOUNT,
            asset=ASSET12,
        ),
        "3dyV+ehncXreLCg6lDZWsYUwUtWoggNOdDDrRCn3YZ/V2rX+6c0ngydfWfgI3HOpM9yfUmrIKzyXNMPW31xzCQ==",
        label="asset12",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABwAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAFYAAAAAAAAAQAAAAAAAAAA
        messages.StellarAllowTrustOp(
            is_authorized=True,
            trusted_account=EXAMPLE_ACCOUNT,
            asset_type=messages.StellarAssetType.ALPHANUM4,
            asset_code="X",
        ),
        "rWJzOXmMIzbu1U5kbmHN3DAI5oa1NTAAdGDr1fU1seNFRQtixIN14WdB61RkIYFrsCltvpQgFhAopR1rQLtOCQ==",
        label="allow",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABwAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAFYAAAAAAAAAAAAAAAAAAAA
        messages.StellarAllowTrustOp(
            is_authorized=False,
            trusted_account=EXAMPLE_ACCOUNT,
            asset_type=messages.StellarAssetType.ALPHANUM4,
            asset_code="X",
        ),
        "JremCHASelebn/FTp6mBoOXW9lEKC8XEjJ5yPp6jfsxnKs1k4k1wUl2B6vZP36IL0cGr8wHQQqH1HSYOl6iBBg==",
        label="revoke",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABgAAAAFYAAAAAAAAACmElgLCDlg2XxI8Eth6HKRVDRDNIbCuDhjUTj5W/WoVAAAAAB3NZQAAAAAAAAAAAA==
        messages.StellarChangeTrustOp(
            asset=ASSET4,
            limit=500_000_000,
        ),
        "GB3HnWD/BnSwzubXv1RV0dGGii6NhN/fSUR6ckbm3vp7FKQa1Sj57p+RpxMHKhh0LItw0+KCchZPF1ZyLzBJDw==",
        label="add",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABgAAAAJBQkNERUZHSElKS0wAAAAAKYSWAsIOWDZfEjwS2HocpFUNEM0hsK4OGNROPlb9ahUAAAAAAAAAAAAAAAAAAAAA
        messages.StellarChangeTrustOp(
            asset=ASSET12,
            limit=0,
        ),
        "SE3fsxsnlujJU4OLuJet56br0vEByqZXijWdJ8AVbwPBBe+xm+Ztk/09htlsJ79tcEELwNSp2xDjGFthTNE6DQ==",
        label="delete",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABAAAAAJBQkNERUZHSElKS0wAAAAAKYSWAsIOWDZfEjwS2HocpFUNEM0hsK4OGNROPlb9ahUAAAABWAAAAAAAAAAphJYCwg5YNl8SPBLYehykVQ0QzSGwrg4Y1E4+Vv1qFQAAAAAdzxaYAAAAAwAAAAQAAAAAAAAAAA==
        messages.StellarCreatePassiveOfferOp(
            selling_asset=ASSET12,
            buying_asset=ASSET4,
            amount=500_111_000,
            price_n=3,
            price_d=4,
        ),
        "y9xb8IgPpkjgFa87I9alTD0mVc6EUcJrD7erZVPVGLdDs7rjh7fVtLAJS7iin85Yle0AwnqqEADYAjVzHzz7Bg==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAwAAAAJBQkNERUZHSElKS0wAAAAAKYSWAsIOWDZfEjwS2HocpFUNEM0hsK4OGNROPlb9ahUAAAABWAAAAAAAAAAphJYCwg5YNl8SPBLYehykVQ0QzSGwrg4Y1E4+Vv1qFQAAAAAdzxaYAAAAAwAAAAQAAAAAAAAFOQAAAAAAAAAA
        messages.StellarManageOfferOp(
            selling_asset=ASSET12,
            buying_asset=ASSET4,
            amount=500_111_000,
            price_n=3,
            price_d=4,
            offer_id=1337,
        ),
        "SB1xWWcwnnGri96c+psQ1tnlpSQNIbvPxEtDlwAd8Pp1a/IXdnv8a3XozgjoRrv3w1uJ09uE+3hoUxiUk5byBg==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAgAAAAFYAAAAAAAAACmElgLCDlg2XxI8Eth6HKRVDRDNIbCuDhjUTj5W/WoVAAAAAB3PFpgAAAAAXVVkJGaxhbhDFS6eIZFR28WJICfsQBAaUXvtXKAwwuAAAAACQUJDREVGR0hJSktMAAAAACmElgLCDlg2XxI8Eth6HKRVDRDNIbCuDhjUTj5W/WoVAAAAAAAB4kAAAAAAAAAAAAAAAAA=
        messages.StellarPathPaymentOp(
            send_asset=ASSET4,
            send_max=500_111_000,
            destination_account=EXAMPLE_ACCOUNT,
            destination_asset=ASSET12,
            destination_amount=123456,
        ),
        "A/ccrRMTEy3GXaZ7Lo5frX3ME5fy3bDMrmYaZ8oPtpPk+cnRStbcSAgdTKnRq/dPGRLfh2btvPJD9ETMe1ajDA==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAACgAAAARkYXRhAAAAAQAAAANhYmMAAAAAAAAAAAA=
        messages.StellarManageDataOp(key="data", value=b"abc"),
        "8itLTzFFEwGXeAeSPeus/GGRu1sC+N1darL8/WERJHUPXKLra7QxBUmcoRvNb1rf0gonWCnZepAhn70R9mVOAw==",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABQAAAAEAAAAAXVVkJGaxhbhDFS6eIZFR28WJICfsQBAaUXvtXKAwwuAAAAABAAAAAQAAAAEAAAAGAAAAAQAAAGQAAAABAAAAAQAAAAEAAAAKAAAAAQAAAFoAAAABAAAAD3d3dy5leGFtcGxlLmNvbQAAAAABAAAAAHIYetuHnEFDRtd8ca+Mzntuqle1KOmZ/ZH+rmtkGGKOAAAAFAAAAAAAAAAA
        messages.StellarSetOptionsOp(
            inflation_destination_account=EXAMPLE_ACCOUNT,
            clear_flags=1,
            set_flags=6,
            master_weight=100,
            low_threshold=1,
            medium_threshold=10,
            high_threshold=90,
            home_domain="www.example.com",
            signer_type=messages.StellarSignerType.ACCOUNT,
            signer_key=EXAMPLE_SIGNER_KEY,
            signer_weight=20,
        ),
        "Yy/iO5/Hjf67PYvxzvdAcc8r+/izKYg++ra/GrMe6KFmPfiKWJXnD2DMfExMcSGt3bMFwT6BBko+WiEr/4PUAQ==",
        label="all",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABQAAAAAAAAAAAAAAAQAAAAEAAAABAAAACgAAAAAAAAABAAAAMgAAAAAAAAAAAAAAAQAAAAFyGHrbh5xBQ0bXfHGvjM57bqpXtSjpmf2R/q5rZBhijgAAAAoAAAAAAAAAAA==
        messages.StellarSetOptionsOp(
            set_flags=1,
            master_weight=10,
            medium_threshold=50,
            signer_type=messages.StellarSignerType.PRE_AUTH,
            signer_key=EXAMPLE_SIGNER_KEY,
            signer_weight=10,
        ),
        "fR0Omce7E6ZcK9VMCTRQjGl3+3yOomlO6aGPaH2EcgwTkrw4iWdkJi3Abkyzoqx2TRYsNjDrmMKflhB++F2ICw==",
        label="some",
    ),
    v(
        # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAJyGHrbh5xBQ0bXfHGvjM57bqpXtSjpmf2R/q5rZBhijgAAAAoAAAAAAAAAAA==
        messages.StellarSetOptionsOp(
            signer_type=messages.StellarSignerType.HASH,
            signer_key=EXAMPLE_SIGNER_KEY,
            signer_weight=10,
        ),
        "HgJas9f4I/o1gneU6+t7fhfdFMttSO57a8P/1wgMQ87ySt3WW/RQvFqqTX+evXmLFb/XZ5A9K3tcw1WLBhSdBQ==",
        label="one",
    ),
)


@pytest.mark.parametrize("operation, signature", VECTORS)
def test_operations(client, operation, signature):
    """Test that each operation can be signed."""
    response = stellar.sign_tx(
        client, DEFAULT_REQUEST, [operation], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        response.public_key.hex()
        == "2f22b9c62f08b774f3ebe6dd6e7db93c3ec2cbde0279561a3d9c5225b8c32292"
    )
    assert b64encode(response.signature).decode() == signature


@pytest.mark.parametrize(
    "start, end, signature",
    (
        (
            # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
            0,
            0,
            "GjUEwL7wGOLPWa3koAdDNq9b1me8elkXeO9um5fT/dv7zjXCSavoMyzWXsCikjkkdYkch6PyBgQUjL0d6RhrDw==",
        ),
        (
            # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
            0,
            1575234180,
            "zzAQiWN6F3XUuwxDx+326FsP0zphqGL+R3DRF/hJc/k0072efcgOUBYL2uCwehBdo5qgWdLcAEXiR6IFlaywCw==",
        ),
        (
            # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
            461535181,
            1575234180,
            "GGmvB49owuJZ+5GA6FCCFoHsj8F+YWojgVEbmFKgqjZobMXcGjyCt8hU1M9nzWFFIVASud/pNKzpzvqwYI2xDQ==",
        ),
        (
            # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
            461535181,
            0,
            "6WrPy52etTfIDKAYnYz/XsvAvKR+FicNfv8uaLqlZakhrb5iT7dxmOAz15D6at/Mnxx0LEEKqsAzG/1+CjaMDg==",
        ),
    ),
)
def test_timebounds(client, start, end, signature):
    request = copy(DEFAULT_REQUEST)
    request.timebounds_start = start
    request.timebounds_end = end
    response = stellar.sign_tx(
        client, request, [EXAMPLE_OPERATION], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert b64encode(response.signature).decode() == signature


def test_memo_text(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAA1IZWxsbywgd29ybGQhAAAAAAAAAQAAAAAAAAABAAAAAF1VZCRmsYW4QxUuniGRUdvFiSAn7EAQGlF77VygMMLgAAAAAAAAAAAdzxaYAAAAAAAAAAA=
    request = copy(DEFAULT_REQUEST)
    request.memo_type = messages.StellarMemoType.TEXT
    request.memo_text = "Hello, world!"
    response = stellar.sign_tx(
        client, request, [EXAMPLE_OPERATION], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "0fMCgbE8/Lf0r1WdjOtYpQThNBmeLrac3a8V2fD80Whzv+1pSY+KgwDbtv2PWX9CCCKGQ51iL7IiMk3zubz1BQ=="
    )


def test_memo_id(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAgAACzpzzi/yAAAAAQAAAAAAAAABAAAAAF1VZCRmsYW4QxUuniGRUdvFiSAn7EAQGlF77VygMMLgAAAAAAAAAAAdzxaYAAAAAAAAAAA=
    request = copy(DEFAULT_REQUEST)
    request.memo_type = messages.StellarMemoType.ID
    request.memo_id = 12345678901234
    response = stellar.sign_tx(
        client, request, [EXAMPLE_OPERATION], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "Rq7LI+SHrHBeD55Tgoj4YAxeJ8Ldu8Mds22xFD+wbDGmElhkvkE1KUUznE2DoOcGraA/Kcah2KiQ5L/DaTDbDA=="
    )


def test_memo_hash(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAwEjRWeJq83vASNFZ4mrze8BI0VniavN7wEjRWeJq83vAAAAAQAAAAAAAAABAAAAAF1VZCRmsYW4QxUuniGRUdvFiSAn7EAQGlF77VygMMLgAAAAAAAAAAAdzxaYAAAAAAAAAAA=
    request = copy(DEFAULT_REQUEST)
    request.memo_type = messages.StellarMemoType.HASH
    request.memo_hash = bytes.fromhex(
        "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"
    )
    response = stellar.sign_tx(
        client, request, [EXAMPLE_OPERATION], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "OVjaU2aKOCSSHFDktWGONJ6aOgjEx6HlQQuqmtqs9opLmjQDO0aajALSMeFNv7hWhvzJGsAQfeqpdDHq6BARBg=="
    )


def test_memo_return(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAABAEjRWeJq83vASNFZ4mrze8BI0VniavN7wEjRWeJq83vAAAAAQAAAAAAAAABAAAAAF1VZCRmsYW4QxUuniGRUdvFiSAn7EAQGlF77VygMMLgAAAAAAAAAAAdzxaYAAAAAAAAAAA=
    request = copy(DEFAULT_REQUEST)
    request.memo_type = messages.StellarMemoType.RETURN
    request.memo_hash = bytes.fromhex(
        "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"
    )
    response = stellar.sign_tx(
        client, request, [EXAMPLE_OPERATION], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "49G1t+0i3kUZ/fn8BQu4mp11ROSq33Wi0GJEzAY1YJlRYvsV1bunf05b11wF/1OQXf9LK4fUCz00rTYEzbcgAQ=="
    )


def test_multiple_operations(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAASwAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAMAAAAAAAAAAAAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAF9eEAAAAAAAAAAAQAAAACQUJDREVGR0hJSktMAAAAACmElgLCDlg2XxI8Eth6HKRVDRDNIbCuDhjUTj5W/WoVAAAAAVgAAAAAAAAAKYSWAsIOWDZfEjwS2HocpFUNEM0hsK4OGNROPlb9ahUAAAAAHc8WmAAAAAMAAAAEAAAAAAAAAAoAAAAEZGF0YQAAAAEAAAADYWJjAAAAAAAAAAAA
    request = copy(DEFAULT_REQUEST)
    request.fee = 300
    operations = [
        messages.StellarCreateAccountOp(
            new_account=EXAMPLE_ACCOUNT, starting_balance=100_000_000
        ),
        messages.StellarCreatePassiveOfferOp(
            selling_asset=ASSET12,
            buying_asset=ASSET4,
            amount=500_111_000,
            price_n=3,
            price_d=4,
        ),
        messages.StellarManageDataOp(key="data", value=b"abc"),
    ]
    response = stellar.sign_tx(
        client, request, operations, ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "ZSGKHi6FLjgOzxuyE2hRWw0ArdF4Bie5GprdsBwiBYYBwVp7t2ex6+5bIyBCyCoYEyW+LABO74THFQzsmFoBAw=="
    )


def test_source_account(client):
    # AAAAAgAAAAAvIrnGLwi3dPPr5t1ufbk8PsLL3gJ5Vho9nFIluMMikgAAAGQAAAAAAAAD6AAAAAEAAAAAG4J3zQAAAABd5CqEAAAAAAAAAAEAAAABAAAAAF1VZCRmsYW4QxUuniGRUdvFiSAn7EAQGlF77VygMMLgAAAAAQAAAABdVWQkZrGFuEMVLp4hkVHbxYkgJ+xAEBpRe+1coDDC4AAAAAAAAAAAHc8WmAAAAAAAAAAA
    operation = copy(EXAMPLE_OPERATION)
    operation.source_account = EXAMPLE_ACCOUNT
    response = stellar.sign_tx(
        client, DEFAULT_REQUEST, [operation], ADDRESS_N, NETWORK_PASSPHRASE
    )
    assert (
        b64encode(response.signature).decode()
        == "Ps6r6f8yFu3IS19JKJNgAsJ3QwWW7YOckCRj96XK5BP3UGlTyI4K025E/+DRba/tiscMKBL52ERHkdSf3A8wCQ=="
    )
