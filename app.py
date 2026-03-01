<div id="final-thermal-v10" style="max-width: 1000px; margin: 20px auto; font-family: 'Segoe UI', sans-serif; background: #fff; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); border: 1px solid #ddd; overflow: hidden;">
    
    <div style="display: flex; background: #f1f3f5; border-bottom: 1px solid #ccc;">
        <button onclick="changeModeV10('fk')" id="b-fk" style="flex: 1; padding: 18px; border: none; cursor: pointer; font-weight: 800; background: #0073aa; color: white;">Flipkart Pro Tool</button>
        <button onclick="changeModeV10('ms')" id="b-ms" style="flex: 1; padding: 18px; border: none; cursor: pointer; font-weight: 800; background: #eee; color: #333;">Meesho Pro Tool</button>
    </div>

    <div style="padding: 30px; display: flex; flex-wrap: wrap; gap: 30px;">
        <div style="flex: 1; min-width: 400px;">
            <div style="border: 2px dashed #0073aa; padding: 40px; text-align: center; border-radius: 12px; background: #f8fbff;">
                <input type="file" id="v10-pdf-input" accept="application/pdf" multiple style="display:none" />
                <button onclick="document.getElementById('v10-pdf-input').click()" style="background:#0073aa; color:white; border:none; padding:15px 30px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:18px;">+ ATTACH PDF LABELS</button>
                <div id="v10-stat" style="margin-top:15px; font-weight:bold; color:#0073aa;">0 Files Ready</div>
            </div>
            
            <div id="v10-queue" style="margin-top:20px; max-height:120px; overflow-y:auto; border:1px solid #eee; border-radius:8px; display:none; background:#fff;"></div>

            <div id="v10-crop-box" style="display:none; margin-top:25px;">
                <p style="font-weight:bold; color:#d35400; margin-bottom:10px;">✂️ Confirm Shipping Label Area:</p>
                <div style="border:3px solid #000; border-radius:10px; overflow:hidden;"><img id="v10-preview-img" style="display:block; max-width:100%;"></div>
            </div>
        </div>

        <div style="width: 320px; background: #fcfcfc; padding: 25px; border-radius: 12px; border: 1px solid #eee;">
            <h4 style="margin:0 0 20px 0; color:#0073aa; font-weight: 800;">Process Settings</h4>
            <div style="display:flex; flex-direction:column; gap:15px; font-size:14px; color:#333;">
                <label style="font-weight:bold;"><input type="checkbox" id="v10-sort" checked> Group by Sold By</label>
                <label style="color:#27ae60; font-weight:900;"><input type="checkbox" id="v10-sum-chk" checked> Summery (Locked Design)</label>
                <hr>
                <label><input type="checkbox" id="v10-inv"> Keep Invoices</label>
            </div>

            <button id="v10-download-btn" style="margin-top:35px; width:100%; padding:20px; background:#218838; color:white; border:none; border-radius:8px; font-weight:900; cursor:pointer; font-size:18px;">
                CROP & DOWNLOAD
            </button>
            <div id="v10-log" style="margin-top:15px; font-size:12px; color:#c0392b; text-align:center; font-weight:bold;">READY</div>
        </div>
    </div>
    <canvas id="v10-canvas" style="display:none;"></canvas>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
<script src="https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js"></script>

<script>
    let v10Queue = [];
    const v10PDFJS = window['pdfjs-dist/build/pdf'];
    v10PDFJS.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

    function changeModeV10(m) {
        document.getElementById('b-fk').style.background = m === 'fk' ? '#0073aa' : '#eee';
        document.getElementById('b-ms').style.background = m === 'ms' ? '#0073aa' : '#eee';
    }

    document.getElementById('v10-pdf-input').onchange = async (e) => {
        const files = Array.from(e.target.files);
        for (let f of files) { v10Queue.push({ name: f.name, data: await f.arrayBuffer() }); }
        updateQueueUI();
        if (v10Queue.length > 0) initV10Cropper(v10Queue[0].data);
    };

    function updateQueueUI() {
        const ui = document.getElementById('v10-queue'); ui.innerHTML = '';
        v10Queue.forEach((f, i) => {
            const div = document.createElement('div');
            div.style = "display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #f1f1f1; font-size:12px;";
            div.innerHTML = `<span>📄 ${f.name}</span><b onclick="removeV10(${i})" style="color:red; cursor:pointer;">✕</b>`;
            ui.appendChild(div);
        });
        document.getElementById('v10-stat').innerText = `${v10Queue.length} Files Attached`;
        ui.style.display = 'block';
    }

    function removeV10(i) { v10Queue.splice(i, 1); updateQueueUI(); }

    async function initV10Cropper(buf) {
        const pdf = await v10PDFJS.getDocument({data: new Uint8Array(buf)}).promise;
        const page = await pdf.getPage(1);
        const canv = document.getElementById('v10-canvas');
        const ctx = canv.getContext('2d');
        const vp = page.getViewport({ scale: 1.0 });
        canv.height = vp.height; canv.width = vp.width;
        await page.render({ canvasContext: ctx, viewport: vp }).promise;
        const node = document.getElementById('v10-preview-img');
        node.src = canv.toDataURL();
        document.getElementById('v10-crop-box').style.display = 'block';
    }

    document.getElementById('v10-download-btn').onclick = async () => {
        if (!v10Queue.length) return;
        const log = document.getElementById('v10-log');
        log.style.color = "#0073aa";
        log.innerText = "⚡ SCANNING CLEAN SKU DATA...";

        const { PDFDocument, rgb, StandardFonts } = PDFLib;
        const outPdf = await PDFDocument.create();
        const fBold = await outPdf.embedFont(StandardFonts.HelveticaBold);
        const fReg = await outPdf.embedFont(StandardFonts.Helvetica);

        let masterRegistry = [];
        let stats = { skus: {}, couriers: {}, sellers: {} };

        for (let obj of v10Queue) {
            const srcDoc = await PDFDocument.load(obj.data);
            const jsDoc = await v10PDFJS.getDocument({data: obj.data}).promise;
            
            for (let i = 1; i <= srcDoc.getPageCount(); i++) {
                const jsP = await jsDoc.getPage(i);
                const textObj = await jsP.getTextContent();
                const rawText = textObj.items.map(s => s.str).join(" ");
                
                let courier = rawText.includes("E-Kart") ? "E-Kart Logistics" : "Other Courier";
                let sellerMatch = rawText.match(/Sold By:\s*([^,]+)/i);
                let seller = sellerMatch ? sellerMatch[1].trim() : "Unknown";
                if (seller.toUpperCase().includes("DEVILSON")) seller = "Devilsons";
                if (seller.toUpperCase().includes("PALAK")) seller = "Palak Enterprises";

                // STRICT SKU LOGIC: Only look for text AFTER "Description"
                let sku = "Unknown SKU";
                let skuMatch = rawText.match(/Description(?:[^1]{0,30}?)1\s+([^|]{5,100})\|/i);
                
                if (skuMatch) {
                    sku = skuMatch[1].trim();
                } else {
                    // Fallback block
                    let fbMatch = rawText.match(/SKU ID\s*\|?\s*Description\s*(?:QTY)?\s*([^|]{5,100})\|/i);
                    if (fbMatch) sku = fbMatch[1].trim();
                }

                let qtyMatch = rawText.match(/QTY\s+(\d+)/i) || rawText.match(/\|\s+(\d+)\s+Use/i);
                let qty = qtyMatch ? parseInt(qtyMatch[1]) : 1;

                stats.skus[sku] = (stats.skus[sku] || 0) + qty;
                stats.couriers[courier] = (stats.couriers[courier] || 0) + 1;
                stats.sellers[seller] = (stats.sellers[seller] || 0) + 1;

                masterRegistry.push({ pageIdx: i-1, seller, courier, rawBuf: obj.data });
            }
        }

        if (document.getElementById('v10-sort').checked) masterRegistry.sort((a, b) => a.seller.localeCompare(b.seller));

        // EMBEDDED DRAW (LOCKED THERMAL CROP)
        for (let item of masterRegistry) {
            const [embeddedLabel] = await outPdf.embedPdf(item.rawBuf, [item.pageIdx]);
            const cropWidth = 550;
            const cropHeight = 400;
            const newThermalPage = outPdf.addPage([cropWidth, cropHeight]);
            
            newThermalPage.drawPage(embeddedLabel, {
                x: -22,
                y: -(842 - cropHeight - 22),
                width: 595,
                height: 842
            });
        }

        // BOLD SUMMERY PAGE (LOCKED DESIGN)
        if (document.getElementById('v10-sum-chk').checked) {
            const sPage = outPdf.addPage([595, 842]);
            sPage.drawText(`Summery - Generated on ${new Date().toLocaleDateString('en-GB')}`, { x: 50, y: 810, size: 12, font: fBold });

            const drawV10Row = (y, ord, qty, sku, isH = false) => {
                const h = 20;
                sPage.drawRectangle({ x: 50, y: y-4, width: 500, height: h, color: isH ? rgb(0.85, 0.85, 0.85) : rgb(1,1,1), borderWidth: 1 });
                sPage.drawLine({ start: { x: 85, y: y-4 }, end: { x: 85, y: y+h-4 }, thickness: 1 });
                sPage.drawLine({ start: { x: 125, y: y-4 }, end: { x: 125, y: y+h-4 }, thickness: 1 });
                sPage.drawText(ord, { x: 55, y: y+3, size: 9, font: fBold });
                sPage.drawText(qty, { x: 92, y: y+3, size: 9, font: fBold });
                sPage.drawText(sku.substring(0, 75), { x: 130, y: y+3, size: 8, font: fBold });
                return y - h;
            };

            let yPos = 780;
            yPos = drawV10Row(yPos, "ORD", "QTY", "SKU", true);
            Object.entries(stats.skus).forEach(([s, q]) => { yPos = drawV10Row(yPos, "1", q.toString(), s); });

            yPos -= 30;
            sPage.drawText(`Total package: ${masterRegistry.length}`, { x: 50, y: yPos, size: 12, font: fBold });

            const drawV10Box = (yS, label, data) => {
                sPage.drawRectangle({ x: 50, y: yS-4, width: 500, height: 20, color: rgb(0.9, 0.9, 0.9), borderWidth: 1 });
                sPage.drawText("Package", { x: 55, y: yS+4, size: 10, font: fBold });
                sPage.drawLine({ start: { x: 125, y: yS-4 }, end: { x: 125, y: yS+16 }, thickness: 1 });
                sPage.drawText(label, { x: 130, y: yS+4, size: 10, font: fBold });
                let cy = yS - 20;
                Object.entries(data).forEach(([n, c]) => {
                    sPage.drawRectangle({ x: 50, y: cy-4, width: 500, height: 20, borderWidth: 1 });
                    sPage.drawText(c.toString(), { x: 75, y: cy+4, size: 10, font: fBold });
                    sPage.drawLine({ start: { x: 125, y: cy-4 }, end: { x: 125, y: cy+16 }, thickness: 1 });
                    sPage.drawText(n, { x: 130, y: cy+4, size: 10, font: fBold });
                    cy -= 20;
                });
                return cy;
            };

            yPos = drawV10Box(yPos - 20, "Courier Partner", stats.couriers);
            drawV10Box(yPos - 20, "Sold By", stats.sellers);
        }

        const bytes = await outPdf.save();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
        link.download = `Final_Perfect_Thermal_Summery.pdf`;
        link.click();
        log.innerText = "✅ SUCCESS! DOWNLOADED.";
    };
</script>
