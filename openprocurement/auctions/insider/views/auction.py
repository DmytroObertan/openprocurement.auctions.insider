# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
    opresource,
    remove_draft_bids
)
from openprocurement.auctions.insider.validation import (
    validate_auction_auction_data,
)
from openprocurement.auctions.dgf.views.financial.auction import (
    FinancialAuctionAuctionResource,
)
from openprocurement.auctions.insider.utils import create_awards, invalidate_empty_bids


@opresource(name='dgfInsider:Auction Auction',
            collection_path='/auctions/{auction_id}/auction',
            path='/auctions/{auction_id}/auction/{auction_lot_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction auction data")
class InsiderAuctionAuctionResource(FinancialAuctionAuctionResource):
    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_post(self):
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        auction = self.request.validated['auction']
        invalidate_empty_bids(auction)
        remove_draft_bids(self.request)
        if any([i.status == 'active' for i in auction.bids]):
            create_awards(self.request)
        else:
            auction.status = 'unsuccessful'
        if save_auction(self.request):
            self.LOGGER.info('Report auction results',
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_patch(self):
        """Set urls for access to auction.
        """
        if apply_patch(self.request, src=self.request.validated['auction_src']):
            self.LOGGER.info('Updated auction urls', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_patch'}))
            return {'data': self.request.validated['auction'].serialize("auction_view")}
